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

"""CPU-only, weight-free smoke test for the PI05 + DynaFLIP PVI injection seam
(maps analysis/2605.30350/design.md onto the lerobot pi05 base).

Covers the pure pieces only — the projection module, config defaults /
validation / registration, the subclass seam overrides, and factory wiring.
The heavy PaliGemma backbone forward is NOT exercised (it needs downloaded
weights), per the foundry §G contract.
"""

import pytest
import torch

from lerobot.policies.factory import get_policy_class, make_policy_config
from lerobot.policies.pi05.configuration_pi05 import PI05Config
from lerobot.policies.pi05.configuration_pi05_dynaflip import PI05DynaflipConfig
from lerobot.policies.pi05.modeling_pi05 import PI05Policy, PI05Pytorch
from lerobot.policies.pi05.modeling_pi05_dynaflip import (
    DynaflipPrefixInjector,
    PI05DynaflipPolicy,
    PI05DynaflipPytorch,
)


def test_injector_projects_feature_to_prefix_tokens():
    # (B, feature_dim) -> (B, num_tokens, hidden_dim)
    injector = DynaflipPrefixInjector(feature_dim=8, hidden_dim=16, num_tokens=2)
    out = injector(torch.randn(4, 8))
    assert out.shape == (4, 2, 16)


def test_injector_single_token_default_dim():
    # DynaFLIP design contract: feature_dim 1536 (DINOv2 CLS+patch-mean), 1 token.
    injector = DynaflipPrefixInjector(feature_dim=1536, hidden_dim=2048, num_tokens=1)
    out = injector(torch.randn(3, 1536))
    assert out.shape == (3, 1, 2048)


def test_config_defaults_reproduce_base_behavior():
    cfg = PI05DynaflipConfig()
    # Default OFF -> identical to vanilla PI05.
    assert cfg.inject_dynaflip is False
    assert cfg.dynaflip_feature_dim == 1536
    assert cfg.dynaflip_num_tokens == 1
    assert cfg.dynaflip_feature_key == "observation.dynaflip_feature"
    # It is a genuine PI05Config subclass (reuses the pi05 processor path).
    assert isinstance(cfg, PI05Config)


def test_config_rejects_out_of_range_values():
    with pytest.raises(ValueError):
        PI05DynaflipConfig(dynaflip_feature_dim=0)
    with pytest.raises(ValueError):
        PI05DynaflipConfig(dynaflip_num_tokens=0)


def test_registered_type_name():
    assert PI05DynaflipConfig().type == "pi05_dynaflip"


def test_seam_overrides_are_in_place():
    # Base defines the behavior-preserving seams ...
    assert hasattr(PI05Pytorch, "_extra_prefix_embeds")
    assert hasattr(PI05Policy, "_build_model")
    # ... and the subclass overrides exactly those seams.
    assert "_extra_prefix_embeds" in PI05DynaflipPytorch.__dict__
    assert "_build_model" in PI05DynaflipPolicy.__dict__
    assert PI05DynaflipPolicy.name == "pi05_dynaflip"


def test_factory_resolves_new_policy_name():
    assert get_policy_class("pi05_dynaflip") is PI05DynaflipPolicy
    cfg = make_policy_config("pi05_dynaflip")
    assert isinstance(cfg, PI05DynaflipConfig)
