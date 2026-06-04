#!/usr/bin/env python

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
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

"""CPU-only, weight-free smoke test for the PI05 + DynaFLIP PVI copy-branch
(maps analysis/2605.30350/design.md onto the lerobot pi05 base).

Covers the pure / structural pieces only — the zero-init projection convention,
config defaults / validation / registration, the subclass seam overrides, and
factory wiring. The copy-branch forward (a full action-expert pass over the
aux + action tokens) and the per-layer injection are NOT exercised: they need
the PaliGemma / gemma weights and the heavy model build, per the foundry §G
contract. Numerical behavior-preservation (zero-init -> identity) is guaranteed
by construction and asserted here at the module level via ``zero_init_linear``.
"""

import pytest
import torch

from lerobot.policies.factory import get_policy_class, make_policy_config
from lerobot.policies.pi05.configuration_pi05 import PI05Config
from lerobot.policies.pi05.configuration_pi05_dynaflip import PI05DynaflipConfig
from lerobot.policies.pi05.modeling_pi05 import PI05Policy, PI05Pytorch
from lerobot.policies.pi05.modeling_pi05_dynaflip import (
    PI05DynaflipPolicy,
    PI05DynaflipPytorch,
    zero_init_linear,
)


def test_zero_init_linear_outputs_zero():
    # PVI zero-init: the residual is EXACTLY zero at init -> identity, so the
    # injected policy equals the frozen base until training learns it in.
    lin = zero_init_linear(8, 16)
    out = lin(torch.randn(4, 8))
    assert out.shape == (4, 16)
    assert torch.count_nonzero(out) == 0


def test_zero_init_linear_learns_after_update():
    # Once perturbed, the projection is a live (non-dead) path.
    lin = zero_init_linear(8, 16)
    with torch.no_grad():
        lin.weight.add_(torch.randn_like(lin.weight))
    assert torch.count_nonzero(lin(torch.randn(4, 8))) > 0


def test_config_defaults_reproduce_base_behavior():
    cfg = PI05DynaflipConfig()
    # Default OFF -> identical to vanilla PI05.
    assert cfg.inject_dynaflip is False
    # Patch-token feature dim (DINOv2-B token width), not the pooled 1536.
    assert cfg.dynaflip_feature_dim == 768
    assert cfg.dynaflip_feature_key == "observation.dynaflip_feature"
    assert isinstance(cfg, PI05Config)


def test_config_rejects_out_of_range_values():
    with pytest.raises(ValueError):
        PI05DynaflipConfig(dynaflip_feature_dim=0)


def test_registered_type_name():
    assert PI05DynaflipConfig().type == "pi05_dynaflip"


def test_class_hierarchy():
    assert issubclass(PI05DynaflipPytorch, PI05Pytorch)
    assert issubclass(PI05DynaflipPolicy, PI05Policy)
    assert PI05DynaflipPolicy.name == "pi05_dynaflip"


def test_base_seams_present():
    # Factory seam for the core model ...
    assert hasattr(PI05Policy, "_build_model")
    # ... and the per-layer expert injection callback hook on the base model
    # (an instance attr defaulting to None; the source wires it in __init__).
    import inspect

    from lerobot.policies.pi05 import modeling_pi05

    src = inspect.getsource(modeling_pi05.PaliGemmaWithExpertModel)
    assert "expert_layer_injector" in src


def test_subclass_overrides_in_place():
    # The copy-branch subclass overrides exactly the seams it needs.
    for name in ("_build_model",):
        assert name in PI05DynaflipPolicy.__dict__
    for name in ("embed_suffix", "_inject_expert_layer", "_compute_copy_hidden", "set_dynaflip_feature"):
        assert name in PI05DynaflipPytorch.__dict__


def test_factory_resolves_new_policy_name():
    assert get_policy_class("pi05_dynaflip") is PI05DynaflipPolicy
    cfg = make_policy_config("pi05_dynaflip")
    assert isinstance(cfg, PI05DynaflipConfig)
