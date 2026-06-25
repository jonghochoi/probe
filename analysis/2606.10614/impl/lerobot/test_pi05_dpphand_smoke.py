#!/usr/bin/env python

# Copyright 2025 Physical Intelligence and The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CPU-only, weight-free smoke test for the pi05_dpphand mapping of
arXiv:2606.10614 ("Dexterous Point Policy").

Covers the pure, importable surface of the patch — the hand-keypoint
data contract, phi_hand / phi_contact, the contact head + composite loss, and
the factory/registration wiring. It deliberately does NOT build the PaliGemma
backbone (that needs downloaded weights / large memory), per the foundry-mode
smoke-test rule.
"""

import pytest
import torch

from lerobot.configs import PreTrainedConfig
from lerobot.policies.pi05.configuration_pi05_dpphand import (
    OBS_HAND_KEYPOINTS,
    PI05DPPHandConfig,
)
from lerobot.policies.pi05.modeling_pi05_dpphand import (
    ContactHead,
    HandKeypointEncoder,
    PI05DPPHandPolicy,
    composite_dpphand_loss,
    contact_bce_loss,
)
from lerobot.policies.pi05.processor_pi05_dpphand import (
    Pi05DPPHandKeypointProcessorStep,
    build_hand_keypoint_vector,
    validate_contact_vector,
)
from lerobot.types import TransitionKey


# ── Config: defaults match the paper / Design, and validation rejects junk ──
def test_config_defaults():
    cfg = PI05DPPHandConfig()
    assert cfg.n_hand_keypoints == 6
    assert cfg.hand_keypoint_dim == 18  # 6 keypoints x 3D (paper §3.3)
    assert cfg.n_fingertips == 5  # contact is per-fingertip, no wrist
    assert cfg.contact_loss_weight == 1.0  # lambda (Eq.2)
    assert cfg.contact_head_detach is True  # stop-gradient at backbone (§3.3)
    assert cfg.use_contact_channel is False  # pretraining has no contact channel
    assert cfg.hand_keypoint_order[0] == "wrist"
    assert tuple(cfg.fingertip_order) == ("thumb", "index", "middle", "ring", "pinky")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"hand_keypoint_dim": 20},  # != 3 * n_hand_keypoints
        {"n_fingertips": 6},  # must be n_hand_keypoints - 1
        {"contact_loss_weight": -1.0},  # lambda must be >= 0
        {"contact_pos_weight": 0.0},  # w_+ must be > 0
    ],
)
def test_config_validation_rejects(kwargs):
    with pytest.raises(ValueError):
        PI05DPPHandConfig(**kwargs)


# ── phi_hand / phi_contact (HandKeypointEncoder) ────────────────────────────
def test_hand_encoder_shapes():
    enc = HandKeypointEncoder(in_dim=18, width=16, hidden_dim=8, n_fingertips=5, use_contact=False)
    out = enc(torch.randn(4, 6, 3))  # (B, 6, 3) accepted
    assert out.shape == (4, 16)
    out_flat = enc(torch.randn(4, 18))  # already-flat (B, 18) accepted
    assert out_flat.shape == (4, 16)


def test_hand_encoder_rejects_wrong_dim():
    enc = HandKeypointEncoder(in_dim=18, width=16, hidden_dim=8, use_contact=False)
    with pytest.raises(ValueError):
        enc(torch.randn(4, 5, 3))  # 15 != 18


def test_contact_projector_zero_init_recovers_hand_token():
    """phi_contact last linear is zero-init → at init the contact-aware hand
    token equals the contact-free token exactly (paper §3.3)."""
    torch.manual_seed(0)
    enc = HandKeypointEncoder(in_dim=18, width=16, hidden_dim=8, n_fingertips=5, use_contact=True)
    hand = torch.randn(3, 6, 3)
    contact = torch.tensor([[1.0, 0, 1, 0, 1], [0, 1, 1, 0, 0], [1, 1, 1, 1, 1]])
    base = enc(hand, contact=None)
    fused = enc(hand, contact=contact)
    assert torch.allclose(base, fused, atol=0, rtol=0)
    # And the last contact linear is genuinely all-zero at init.
    assert torch.count_nonzero(enc.contact_proj[-1].weight) == 0
    assert torch.count_nonzero(enc.contact_proj[-1].bias) == 0


# ── psi_ct (ContactHead) + composite loss (Eq.2) ────────────────────────────
def test_contact_head_shape():
    head = ContactHead(width=16, n_fingertips=5)
    logits = head(torch.randn(2, 8, 16))  # (B, H, width) -> (B, H, 5)
    assert logits.shape == (2, 8, 5)


def test_composite_loss_reduces_to_main_when_lambda_zero():
    main = torch.tensor(1.2345)
    logits = torch.randn(2, 4, 5)
    target = (torch.rand(2, 4, 5) > 0.5).float()
    assert torch.allclose(composite_dpphand_loss(main, logits, target, contact_loss_weight=0.0), main)
    # With lambda=1 the BCE term strictly increases the objective.
    assert composite_dpphand_loss(main, logits, target, contact_loss_weight=1.0) > main


def test_contact_loss_stop_gradient_matches_config_flag():
    """contact_head_detach=True must block gradient to the backbone tensor;
    False must let it through (mirrors PI05DPPHandPytorch.contact_logits_from_suffix)."""
    head = ContactHead(width=16, n_fingertips=5)
    target = torch.zeros(2, 4, 5)

    for detach in (True, False):
        hidden = torch.randn(2, 4, 16, requires_grad=True)
        used = hidden.detach() if detach else hidden
        loss = contact_bce_loss(head(used), target)
        loss.backward()
        if detach:
            assert hidden.grad is None
        else:
            assert hidden.grad is not None


# ── Data contract (processor) ───────────────────────────────────────────────
def test_build_hand_keypoint_vector():
    assert build_hand_keypoint_vector(torch.randn(2, 6, 3), 6).shape == (2, 18)
    assert build_hand_keypoint_vector(torch.randn(2, 18), 6).shape == (2, 18)
    with pytest.raises(ValueError):
        build_hand_keypoint_vector(torch.randn(2, 5, 3), 6)


def test_validate_contact_vector():
    validate_contact_vector(torch.tensor([[0.0, 1, 0, 1, 1]]), 5)
    with pytest.raises(ValueError):
        validate_contact_vector(torch.tensor([[0.0, 1, 0, 1]]), 5)  # wrong length
    with pytest.raises(ValueError):
        validate_contact_vector(torch.tensor([[0.0, 1, 0, 1, 2]]), 5)  # non-binary


def test_processor_step_flattens_hand_keypoints():
    step = Pi05DPPHandKeypointProcessorStep(use_contact=False)
    transition = {TransitionKey.OBSERVATION: {OBS_HAND_KEYPOINTS: torch.randn(2, 6, 3)}}
    out = step(transition)
    assert out[TransitionKey.OBSERVATION][OBS_HAND_KEYPOINTS].shape == (2, 18)


# ── Factory / registration ──────────────────────────────────────────────────
def test_config_is_registered():
    assert PreTrainedConfig.get_choice_class("pi05_dpphand") is PI05DPPHandConfig


def test_policy_name_resolves_via_factory():
    from lerobot.policies.factory import get_policy_class

    assert get_policy_class("pi05_dpphand") is PI05DPPHandPolicy
    assert PI05DPPHandPolicy.name == "pi05_dpphand"
    assert PI05DPPHandPolicy.config_class is PI05DPPHandConfig


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
