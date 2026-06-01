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

"""CPU smoke test for the Arm-Hand Feature Enhancement reproduction (arXiv:2511.00139 §7.3).

This is PROBE's *executable* foundry artifact — the runnable counterpart of
``impl.patch``. The validation §🧬 check installs the foundry at its pinned commit
(`scripts/ensure-foundry-runtime.sh lerobot`), applies ``impl.patch`` to that
checkout, and runs this file with pytest. No GPU, no checkpoint, no HF
download: it validates the pure pieces (enhancer shapes, index masking,
composite loss + backprop, Eq. (12) recovery) and the config/factory wiring.
The heavy PaliGemma-backed forward is left to a real training run.

The paper's backbone is π0; this reproduction targets pi05 as a deliberate
foundry-base substitution (the ``z_share`` action-expert hook is identical, so
the enhancement math below is backbone-independent).
"""

import pytest
import torch

from lerobot.configs import PreTrainedConfig
from lerobot.policies.factory import get_policy_class, make_policy_config
from lerobot.policies.pi05.configuration_pi05_enhance import PI05EnhanceConfig
from lerobot.policies.pi05.modeling_pi05_enhance import (
    ArmHandFeatureEnhancer,
    PI05EnhancePolicy,
    build_index_masks,
    compute_feature_enhancement_loss,
)


def test_feature_enhancer_shapes():
    d_s, a = 64, 32
    enhancer = ArmHandFeatureEnhancer(d_s=d_s, max_action_dim=a)
    z_share = torch.randn(2, 4, d_s)
    v_main, v_arm, v_hand = enhancer(z_share)
    for v in (v_main, v_arm, v_hand):
        assert v.shape == (2, 4, a)


def test_index_masks_paper_contract():
    """Paper's πuni action vector: UR3e 6-DoF arm + 12-DoF hand = 18, padded to max_action_dim=32."""
    arm_dim, original_action_dim, a = 6, 18, 32
    arm_mask, hand_mask = build_index_masks(arm_dim, original_action_dim, a)
    assert arm_mask.shape == (a,)
    assert torch.all(arm_mask[:6] == 1.0)
    assert torch.all(arm_mask[6:] == 0.0)
    assert torch.all(hand_mask[6:18] == 1.0)
    assert torch.all(hand_mask[:6] == 0.0)
    assert torch.all(hand_mask[18:] == 0.0)  # padding dims zero
    assert torch.all(arm_mask * hand_mask == 0.0)  # disjoint
    assert arm_mask.sum().item() == 6
    assert hand_mask.sum().item() == 12


def test_composite_loss_finite_and_backprop():
    d_s, a = 64, 32
    enhancer = ArmHandFeatureEnhancer(d_s=d_s, max_action_dim=a)
    z_share = torch.randn(3, 5, d_s)
    u_t = torch.randn(3, 5, a)
    arm_mask, hand_mask = build_index_masks(6, 18, a)

    v_main, v_arm, v_hand = enhancer(z_share)
    losses = compute_feature_enhancement_loss(
        v_main, v_arm, v_hand, u_t, arm_mask, hand_mask, aux_loss_weight=1.0
    )

    assert losses.shape == (3, 5, a)
    assert torch.isfinite(losses).all()

    losses.mean().backward()
    for name in ("H_main", "E_arm", "H_hand"):
        module = getattr(enhancer, name)
        grads = [p.grad for p in module.parameters() if p.grad is not None]
        assert grads, f"no grad on {name}"
        assert all(torch.isfinite(g).all() for g in grads)


def test_aux_weight_zero_recovers_main_only_loss():
    """Eq. (12) with lambda=0 must reduce to the bare main flow-matching loss."""
    d_s, a = 32, 16
    enhancer = ArmHandFeatureEnhancer(d_s=d_s, max_action_dim=a)
    z_share = torch.randn(2, 3, d_s)
    u_t = torch.randn(2, 3, a)
    arm_mask, hand_mask = build_index_masks(6, 10, a)
    v_main, v_arm, v_hand = enhancer(z_share)

    composite = compute_feature_enhancement_loss(
        v_main, v_arm, v_hand, u_t, arm_mask, hand_mask, aux_loss_weight=0.0
    )
    main_only = (v_main - u_t) ** 2
    assert torch.allclose(composite, main_only)


def test_config_defaults_and_validation():
    cfg = PI05EnhanceConfig()
    assert cfg.feature_enhancement is False  # πuni-origin by default
    assert cfg.arm_dim == 6  # UR3e 6-DoF (Design 데이터 계약)
    assert cfg.aux_loss_weight == 1.0  # paper-silent default (§3.4.2)

    with pytest.raises(ValueError):
        PI05EnhanceConfig(arm_dim=999)
    with pytest.raises(ValueError):
        PI05EnhanceConfig(aux_loss_weight=-1.0)


def test_factory_registration_and_class_resolution():
    assert "pi05_enhance" in PreTrainedConfig.get_known_choices()
    assert PreTrainedConfig.get_choice_class("pi05_enhance") is PI05EnhanceConfig
    assert make_policy_config("pi05_enhance").type == "pi05_enhance"
    assert get_policy_class("pi05_enhance") is PI05EnhancePolicy
