# SUPPLEMENT — артефакты, на которых держатся числа рукописи

Это приложение к [`paper.md`](paper.md). Оно не пересказывает результаты: здесь
только список артефактов с размерами и sha256, собранный обходом каталогов
скриптом [`scripts/make_artifact_table.py`](../scripts/make_artifact_table.py).

- **Как проверить:** `python scripts/make_artifact_table.py` печатает таблицу;
  тест `test_artifact_table.py` сверяет её с этим файлом, поэтому таблица не
  может разойтись с диском.
- **Классы:** `canonical` — файлы, на которых держатся числа (перепись,
  замороженные центроиды, возмущения); `derived` — сводки и агрегаты;
  `experimental` — exploratory-артефакты (не канон, но источник чисел для
  соответствующих отчётов); `figure` — рисунки рукописи; `index` — машинные
  реестры.
- **Чего здесь нет:** весов (`.pt` в git не едут, индекс — `lab/checkpoints.json`),
  построчных `*_rows.jsonl` (локальные), внешних артефактов Colab (см. §6/§7
  рукописи).
- **Полные тексты чужих статей** не хранятся ни здесь, ни в `library/`: только
  метаданные и DOI (см. [`library/publications/README.md`](../library/publications/README.md)).

## Таблица

<!-- artifacts:start -->
| Артефакт | Тип | Байт | sha256 |
| --- | --- | ---: | --- |
| [`lab/checkpoints.json`](../lab/checkpoints.json) | index | 3608 | `ab04638610b1d9ac31ec3c0aef4fb516157edb06b4579cf98a87380b2e39ec59` |
| [`lab/registry.json`](../lab/registry.json) | index | 208449 | `cc789461bb309668e3e4fbebbab9b8e21ef62477f56a34da1e558358b333481f` |
| [`morphogenesis/experiments/E01_criticality/lyapunov_scan.json`](../morphogenesis/experiments/E01_criticality/lyapunov_scan.json) | other | 1610 | `7db6283ea34a67927c31515e6aceb7f02c42e1124ea35d4800207dbaa51ead18` |
| [`morphogenesis/experiments/E01_criticality/results.json`](../morphogenesis/experiments/E01_criticality/results.json) | other | 2885 | `a00a7272b24bcc22828abaf281f939d97518b8c59dadbd6fe0158a00a623ef22` |
| [`morphogenesis/experiments/E02_pattern/collapse_probe.json`](../morphogenesis/experiments/E02_pattern/collapse_probe.json) | other | 22589 | `1574a6711fe997dbc59dd602f03123b02cb2a83cddc2d031b7d9f7d2ad424b6e` |
| [`morphogenesis/experiments/E02_pattern/delta_profile.json`](../morphogenesis/experiments/E02_pattern/delta_profile.json) | other | 1075 | `0128e7279e49ab939d455f4de141bd60d1f7b1d666e90b4af24aa683a51d8e38` |
| [`morphogenesis/experiments/E02_pattern/gate_layer1.json`](../morphogenesis/experiments/E02_pattern/gate_layer1.json) | other | 16783 | `1c7dab8014f7c4ab189e584e5ed6796907e51e7467bacf27aa56844b5d3a14f7` |
| [`morphogenesis/experiments/E02_pattern/gate_layer1_attempt1_failed.json`](../morphogenesis/experiments/E02_pattern/gate_layer1_attempt1_failed.json) | other | 6825 | `a3499bad81c1db6436b5fc2fdb48a7cae6fbf2780075a08ace9534664536f96d` |
| [`morphogenesis/experiments/E02_pattern/results.json`](../morphogenesis/experiments/E02_pattern/results.json) | other | 262014 | `19b7133b89ed7ab1cf08ce11bcabfdf62416431e43540cd7ba30427c28073b44` |
| [`morphogenesis/experiments/E02_pattern/threshold_probe.json`](../morphogenesis/experiments/E02_pattern/threshold_probe.json) | other | 142837 | `f96ebd39b26f99837d02bde0a46c77c332c2db122979077f2ebde80e3867ef35` |
| [`morphogenesis/experiments/E02_pattern/wp4_ablations.json`](../morphogenesis/experiments/E02_pattern/wp4_ablations.json) | other | 838136 | `9a088ea87975e9073281d9986fb8102c785cbfa61549bd806b3ddca215403d99` |
| [`morphogenesis/experiments/E02_pattern/wp4_reach_probe.json`](../morphogenesis/experiments/E02_pattern/wp4_reach_probe.json) | other | 321076 | `d813119620bbe545996b8b890512d5b0d5f98a6730da841b45228436fed68a6f` |
| [`morphogenesis/experiments/E02_pattern/wp4_reach_probe_R9_s1000.json`](../morphogenesis/experiments/E02_pattern/wp4_reach_probe_R9_s1000.json) | other | 107263 | `ea0a6b2118f391174b47f836edd25fddafcf5365b4e0bfb7114b56c28117be8f` |
| [`morphogenesis/experiments/E02_pattern/wp4_reach_probe_s1000.json`](../morphogenesis/experiments/E02_pattern/wp4_reach_probe_s1000.json) | other | 204464 | `22868e167d3f2a8a49da8e90253c597710b4ae28f99dba5bc4ea7e735f5a7baf` |
| [`morphogenesis/experiments/E02_pattern/wp4_reach_probe_s2000.json`](../morphogenesis/experiments/E02_pattern/wp4_reach_probe_s2000.json) | other | 96636 | `7f3f0f700198f7e7a2d7a6f0438e56e151dc9fd5e32849f1e02bdf2fb47b11a4` |
| [`morphogenesis/experiments/E02b_morphospace/alive_open_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/alive_open_exploratory.json) | experimental | 2755 | `69b8bb91471d0a31190ed7a822c373a44204ab82a15f0a6625db3e880062e6e4` |
| [`morphogenesis/experiments/E02b_morphospace/asymmetry_sides_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/asymmetry_sides_exploratory.json) | experimental | 1225 | `31e8c13634a3056dc688685712350168c220638b46eaa52317efee6df2e47787` |
| [`morphogenesis/experiments/E02b_morphospace/asymmetry_variance_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/asymmetry_variance_exploratory.json) | experimental | 3445 | `2763f521a9c53248a77943529bd3d0fa152395024a0cd6352f4072bff46f4c48` |
| [`morphogenesis/experiments/E02b_morphospace/asymmetry_variance_retry_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/asymmetry_variance_retry_exploratory.json) | experimental | 2919 | `701d7b06148d32f90c07737da6e1ebe7e89f7b89b8c5b1c28f7e59691c0e9af9` |
| [`morphogenesis/experiments/E02b_morphospace/basin_crossinit_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/basin_crossinit_exploratory.json) | experimental | 32635 | `bf681c7a82ca214767cf09825824af8292705b54f56b4d12c8298c5554c92ba3` |
| [`morphogenesis/experiments/E02b_morphospace/basin_reverse_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/basin_reverse_exploratory.json) | experimental | 22778 | `497613e0cc0dd52c6fff7eee3f3da34dd267e55a38b73a34a758b940821db6f8` |
| [`morphogenesis/experiments/E02b_morphospace/body_integrity_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/body_integrity_exploratory.json) | experimental | 352084 | `7ba36c3dc503f9c80d4e6b60fc9c4b45e8e938345d0a5f20413d950d5a11c191` |
| [`morphogenesis/experiments/E02b_morphospace/carrier_ch13_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/carrier_ch13_exploratory.json) | experimental | 506 | `2c5017704d49d32f55bf43925554d8d9f9031ce6084736a8a04d96b117c866b0` |
| [`morphogenesis/experiments/E02b_morphospace/carrier_ch15_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/carrier_ch15_exploratory.json) | experimental | 611 | `e41a177d2ff8e15526f2a530e961f464d87ac6af6e70fafa9f6028a7bfea2b20` |
| [`morphogenesis/experiments/E02b_morphospace/carrier_pairs_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/carrier_pairs_exploratory.json) | experimental | 7462 | `279ca0c078b8a83b17b560217cbc6c5e3a540036c0830e39914353186312ce4c` |
| [`morphogenesis/experiments/E02b_morphospace/carriers2_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/carriers2_exploratory.json) | experimental | 7177 | `f0d20e8ec315bbc40d43e84109e8411cd1a9cd32a8bc1d3cb54196012d20bcdc` |
| [`morphogenesis/experiments/E02b_morphospace/census.json`](../morphogenesis/experiments/E02b_morphospace/census.json) | canonical | 14965634 | `3def0a1056ea451332997c53fc597dc44f5def960c13c55672f3401147ebb12f` |
| [`morphogenesis/experiments/E02b_morphospace/channel_memory_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/channel_memory_exploratory.json) | experimental | 339611 | `494a62d0dedd55a3a27c698603a858ccc60f8df2fac3e73577d02e9077b849dc` |
| [`morphogenesis/experiments/E02b_morphospace/checkpoint_provenance_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/checkpoint_provenance_exploratory.json) | experimental | 21369 | `b8100d7b646236ec9ea6710147f07cb972f9b74487c8fcb95635b6f5e10e750f` |
| [`morphogenesis/experiments/E02b_morphospace/class_centroids_frozen.json`](../morphogenesis/experiments/E02b_morphospace/class_centroids_frozen.json) | canonical | 7038 | `a2d5c1b20b9c53b47498bdf6ceafef08bb000e4bff0c63a30dc7d4e1e884a270` |
| [`morphogenesis/experiments/E02b_morphospace/closures_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/closures_exploratory.json) | experimental | 19208 | `53dee64a787f83b25de78015d95350b933718ae32d2255db878e0cdf9540de4f` |
| [`morphogenesis/experiments/E02b_morphospace/cluster_robustness_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/cluster_robustness_exploratory.json) | experimental | 10725 | `cb6511af3d519a3263413005e5582416cbe850fa73611a9b027e00c73e6c51cd` |
| [`morphogenesis/experiments/E02b_morphospace/clusters3_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/clusters3_exploratory.json) | experimental | 7416 | `b723897d363ebe0c82306e344a832545a04f493e4771295ecf42f09bae9c855e` |
| [`morphogenesis/experiments/E02b_morphospace/fragment_nucleogenesis_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/fragment_nucleogenesis_exploratory.json) | experimental | 1300734 | `44d13c7f04bd6f294578eccceb32da7564d467394db84e161b8eec7d6ef3b8a6` |
| [`morphogenesis/experiments/E02b_morphospace/generic_class_distance_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/generic_class_distance_exploratory.json) | experimental | 6389 | `4bfdac8e6b891e508029fa8c573e09935c758e4b6b60097cbe199d4f89915522` |
| [`morphogenesis/experiments/E02b_morphospace/geometric_lesion_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/geometric_lesion_exploratory.json) | experimental | 18620 | `08673d039206b3ae72959cd1f602b8667dd9e22d380f36d5629b5c162e0a8bc6` |
| [`morphogenesis/experiments/E02b_morphospace/geometric_lesion_rep_ema0_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/geometric_lesion_rep_ema0_exploratory.json) | experimental | 267804 | `02aa441b856e8642c41554f5d35ea7a9ca012e6732e68b323491412e2a7edf56` |
| [`morphogenesis/experiments/E02b_morphospace/geometric_lesion_rep_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/geometric_lesion_rep_exploratory.json) | experimental | 266616 | `6e2cc2d2f1b29c2cd93fad1925e6126c4ba1dd4435c6cd217b29d4b0cebe18e5` |
| [`morphogenesis/experiments/E02b_morphospace/geometry_of_form_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/geometry_of_form_exploratory.json) | experimental | 83598 | `09576daf9ddd27f3512e106115d2f6132693f40b9319ed06fd98c2f855e5e7c6` |
| [`morphogenesis/experiments/E02b_morphospace/heldout_seeds_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/heldout_seeds_exploratory.json) | experimental | 2431542 | `9530e03aeb5bc632bc250397eb07e168d73c5b122749c868880386e84cb6c1ae` |
| [`morphogenesis/experiments/E02b_morphospace/left_outcomes_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/left_outcomes_exploratory.json) | experimental | 1728 | `c5ab7a8092710518b2cd74e8cf487209228b2bb43f2269cacb509781b6ccc6ae` |
| [`morphogenesis/experiments/E02b_morphospace/lesion_core_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/lesion_core_exploratory.json) | experimental | 3077 | `8b98088fed85adf08462d2c39170c02868ab8ad4ff7e15ef6fdedc4993b419a9` |
| [`morphogenesis/experiments/E02b_morphospace/lesion_minimal_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/lesion_minimal_exploratory.json) | experimental | 10165 | `7c36af8fed2640e359e1ec8aa9a744109ef9c881283a77490ae3575e96f54a7c` |
| [`morphogenesis/experiments/E02b_morphospace/lesion_necessity_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/lesion_necessity_exploratory.json) | experimental | 1449 | `214098ac99aa2c0cb2a225bb21f08e4edac704da8bcfc53e478917e80f14ea3c` |
| [`morphogenesis/experiments/E02b_morphospace/long_horizon_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/long_horizon_exploratory.json) | experimental | 854721 | `660a80b923994b4b285362709c9d01d9d241e1ae4d363cf68215fbf7f255c01e` |
| [`morphogenesis/experiments/E02b_morphospace/patch_identity_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/patch_identity_exploratory.json) | experimental | 16422 | `ffe3dc9730fe27ac7246a363b210c2d926ad8b88b5dc0617d9e72522ae572cda` |
| [`morphogenesis/experiments/E02b_morphospace/patch_identity_long_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/patch_identity_long_exploratory.json) | experimental | 13076 | `51d6283af9afab64e8fd5ea6e5256689b4c6609b99a80f21d0db2f72be4338dc` |
| [`morphogenesis/experiments/E02b_morphospace/patch_transplant_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/patch_transplant_exploratory.json) | experimental | 336477 | `e01340b74b4adc7d963a4921f084e0734a5123e08e1b2c3aabebe8953759fcd4` |
| [`morphogenesis/experiments/E02b_morphospace/perturbations.json`](../morphogenesis/experiments/E02b_morphospace/perturbations.json) | canonical | 1839229 | `1b50a426cc804173710f9fcf61527c426f636c1af0b3c49d8da09e7941bc0ec5` |
| [`morphogenesis/experiments/E02b_morphospace/pilot.json`](../morphogenesis/experiments/E02b_morphospace/pilot.json) | other | 575008 | `a86799dc5193332fb9196baadd3095d1e0f8464394a2c40ab7e6e6ed332ce94b` |
| [`morphogenesis/experiments/E02b_morphospace/prototype_reproducibility_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/prototype_reproducibility_exploratory.json) | experimental | 2512 | `22fc11921949e437ca68803a7851fd57aeb2d9ac369dacc2cf730feb4c19f8c9` |
| [`morphogenesis/experiments/E02b_morphospace/r11_bistability_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/r11_bistability_exploratory.json) | experimental | 34876 | `f79fe5bbcc74a9cc2c5e465f388367c62a728e168b81fab2edd43a53f92e6f39` |
| [`morphogenesis/experiments/E02b_morphospace/transient_class_analysis_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/transient_class_analysis_exploratory.json) | experimental | 8760 | `855f4ca52c530608b5838e2d7566f43c31719860368b1340469cc7879a4573a4` |
| [`morphogenesis/experiments/E02b_morphospace/transition_matrix_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/transition_matrix_exploratory.json) | experimental | 112557 | `21371b6ac856e918a47ea61fa24d26ed6a5a0c0efd08d0b36b0ff79f65fd1268` |
| [`morphogenesis/experiments/E02b_morphospace/transition_matrix_rep_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/transition_matrix_rep_exploratory.json) | experimental | 1019572 | `eebc775db0fac6f3db62a504ebe259b5153ad2ab994a500e6a4a5111d6f9b665` |
| [`morphogenesis/experiments/E02b_morphospace/untrained_recovery_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/untrained_recovery_exploratory.json) | experimental | 148483 | `867b2e50908efd7fac1c081c6b314d2eadfd747f7eff0098386af29907fe921d` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32long_3000.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32long_3000.json) | derived | 7897221 | `512a3791c4f3fcb309fc4cb88e4ca3f1d800e9d783067eb4ed196c2288dcd503` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32long_4000.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32long_4000.json) | derived | 10316356 | `141433f21fd15bf75a698e6c23061c0c0703401b73ae56491ac79b5a7da32230` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32traj_1000.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32traj_1000.json) | derived | 3743799 | `5a2908780e38d18112df2f0b473c1445e1f548e43dc2942827cb6b9c20bcb590` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32traj_2000.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32traj_2000.json) | derived | 6683470 | `0142be0ba50abd8148df555ca683ec06a2b4a26bd13163592963b462c57d459c` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32traj_3000.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32traj_3000.json) | derived | 9627242 | `45d81968f51983647cb1ea4be7f6f7e477e9b19d77f1f7c91e3e695c08b09537` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32traj_500.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32traj_500.json) | derived | 2276173 | `966b876400a2c2bb3358f44e19e24e18460258efa33e732f5560eac621f9e310` |
| [`morphogenesis/experiments/E02c_replication/census_e02c.json`](../morphogenesis/experiments/E02c_replication/census_e02c.json) | derived | 6163032 | `5d2122b45a13dc121288912c1f8fc0507d131044b5dc9a6ed340bed7c40f6234` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_data404.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_data404.json) | derived | 3796966 | `47a59a4a096c882c35f959c7dfe43b00a5a36a1c71c00116213df41f04936ab5` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_s4000.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_s4000.json) | derived | 4096367 | `493ee6f7d93d2c6a430551592655fb7c9132fb4fd81e10f66dd687d1b868871f` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed101.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed101.json) | derived | 5389684 | `9cdbe9f1beaf8b12e50a79964efdd53eb920287bf4b43849044e22fa96fae298` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed202.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed202.json) | derived | 5280727 | `152621a78f117da8a48fc5473aefde7e65901a9bd2b1fd1badb5cdef5eb0d39a` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed42.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed42.json) | derived | 4096059 | `d9dcb66ae43ffc131005e9148283085fdf4f6c88667b27b3a70992dbd746eed9` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed42_tf32on.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed42_tf32on.json) | derived | 4096059 | `823ffc29a61bbf055eecf5ef5c2f8b3774af28e5b551eea5f6a80b34e766015f` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_randinit.json`](../morphogenesis/experiments/E02c_replication/census_e02c_randinit.json) | derived | 4096955 | `61f35fc2369f3eb75118f9e91f2562e2d524233be120a3796feef9a93976131a` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_scan_seed101.json`](../morphogenesis/experiments/E02c_replication/census_e02c_scan_seed101.json) | derived | 6719673 | `77b07f599038964e26b690efa4ce191709a3476679fe90aa3eecb414ebcd4181` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_seed42repro.json`](../morphogenesis/experiments/E02c_replication/census_e02c_seed42repro.json) | derived | 3917831 | `c475eec2dc230bd84c52cab8796f0f7cab5cbef87436cfd29d87d6fc105a1a39` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_seed42repro_frozen.json`](../morphogenesis/experiments/E02c_replication/census_e02c_seed42repro_frozen.json) | derived | 4096370 | `88bf50ec0526323cf1825db0dfd9e3f0cadb1355b7452adede41f1a491514108` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_seeddec_A.json`](../morphogenesis/experiments/E02c_replication/census_e02c_seeddec_A.json) | derived | 3925940 | `a078c886804acfa8a40e2bb977e86fa5cea75fcbbfe6bd06bd5f303ac5815194` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_seeddec_B.json`](../morphogenesis/experiments/E02c_replication/census_e02c_seeddec_B.json) | derived | 4097429 | `ee6e461181d91739f3779b4673f050bb3a97e4b66ef2127307ec86f8363ed2cc` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_seeddec_wave2.json`](../morphogenesis/experiments/E02c_replication/census_e02c_seeddec_wave2.json) | derived | 7896900 | `a9ce04c76b0464b2e44b1769d582b9aa4fdc67cdf26773f6d2f7152254b38f5e` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_tf32_s4000.json`](../morphogenesis/experiments/E02c_replication/census_e02c_tf32_s4000.json) | derived | 3796895 | `3b5239dca3ba3b16bbf561860abda21d015ec0935810521aa8edd94fe4c0c41e` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_transient.json`](../morphogenesis/experiments/E02c_replication/census_e02c_transient.json) | derived | 7782096 | `1d67633a063a0e7c7ab222ee39d8509df10e154084776e4fc07094ddd60a4ad9` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_transient_fp32.json`](../morphogenesis/experiments/E02c_replication/census_e02c_transient_fp32.json) | derived | 8046416 | `1a3037d595d65504f4d9648da4adfb760bf764cfc7f2593206273697e437d522` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_transient_seed101.json`](../morphogenesis/experiments/E02c_replication/census_e02c_transient_seed101.json) | derived | 7865852 | `de25fddd19c2b7cbdde46d0a3b0281e9f20105b070c4bbcc687dd96a78b66c71` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_transient_seed202.json`](../morphogenesis/experiments/E02c_replication/census_e02c_transient_seed202.json) | derived | 8040542 | `0b250e5d3f8a728092bb20f2e647234704e1de4887e97be5f4c2fd3d21061c2a` |
| [`morphogenesis/experiments/E02c_replication/curve_tf32long.json`](../morphogenesis/experiments/E02c_replication/curve_tf32long.json) | other | 815 | `a446b04fa9334a2a03f982dc5d13f080baa9ca9920df9cef4c7593fb57479662` |
| [`morphogenesis/experiments/E02c_replication/curve_tf32traj.json`](../morphogenesis/experiments/E02c_replication/curve_tf32traj.json) | other | 1967 | `ad3ab8fc614b20ba954014438e2426af0fd44113777b8b48074ddbc46a22cd19` |
| [`morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s2000_seed42_tf32_boundary.json`](../morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s2000_seed42_tf32_boundary.json) | other | 7909 | `1dc73a503ef1013d78e54238e3263ed6e72badd9ba79c75dbc908190cbc62e1c` |
| [`morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s2000_seed42_tf32_randmask.json`](../morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s2000_seed42_tf32_randmask.json) | other | 2570 | `7cef8ef50965436a0755ae44557ebdf1e3e2fcbdc45b9e4ce363587101574e94` |
| [`morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_fp32_boundary.json`](../morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_fp32_boundary.json) | other | 8038 | `0365dce53c2f2f8e1d0498a73d3ca2d75f9672d94f2a66f2b14eae7a1cdfa441` |
| [`morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_tf32_boundary.json`](../morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_tf32_boundary.json) | other | 7851 | `f2fad073375a9ef2ce79d48db0c848d943bfecf80f6827f16a65f76bf94ff6b0` |
| [`morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_tf32_randmask.json`](../morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_tf32_randmask.json) | other | 2648 | `3e530053a61699ec4bad11e5c6c7d45456ac321c808b18d41bacb0d4521706b2` |
| [`morphogenesis/experiments/E02c_replication/morphometry_holes_sponge101.json`](../morphogenesis/experiments/E02c_replication/morphometry_holes_sponge101.json) | other | 10003 | `62ecf05c412a93e54d6fda6773ea4d540d835eae9101f3723d7c6379e23b5802` |
| [`morphogenesis/experiments/E02c_replication/morphometry_holes_sponge42.json`](../morphogenesis/experiments/E02c_replication/morphometry_holes_sponge42.json) | other | 10006 | `554753e4457c0f02b0684d61f47266bbf5e3f92be7f152c556a563c48acbea28` |
| [`morphogenesis/experiments/E02c_replication/randmask_density_020.json`](../morphogenesis/experiments/E02c_replication/randmask_density_020.json) | other | 2573 | `706f208f067ef91cc074030dd5e7df46b701ee3f5a6dd9a333210c26df9b1cd5` |
| [`morphogenesis/experiments/E02c_replication/randmask_density_035.json`](../morphogenesis/experiments/E02c_replication/randmask_density_035.json) | other | 2594 | `2f232eb90bf3fdc4bce82a64d01547f55bf5bf4b4c3ffc5bf46356c54fb47364` |
| [`morphogenesis/experiments/E02c_replication/randmask_density_050.json`](../morphogenesis/experiments/E02c_replication/randmask_density_050.json) | other | 2575 | `20728dbfb39a0768c8fd2871e114ef6cd863744cc36de2d6dd3ffa6ae47d5fb5` |
| [`morphogenesis/experiments/E02c_replication/randmask_density_065.json`](../morphogenesis/experiments/E02c_replication/randmask_density_065.json) | other | 2553 | `f8eb494cb770234cd44f56ed7025dbd283349a0f2550b63d4917c3a863f5f488` |
| [`morphogenesis/experiments/E02c_replication/randmask_density_080.json`](../morphogenesis/experiments/E02c_replication/randmask_density_080.json) | other | 2570 | `7cef8ef50965436a0755ae44557ebdf1e3e2fcbdc45b9e4ce363587101574e94` |
| [`morphogenesis/experiments/E02c_replication/randmask_du3000_d035.json`](../morphogenesis/experiments/E02c_replication/randmask_du3000_d035.json) | other | 2586 | `9beb74ca62c4e742f3569ba47f24f55ccbd6ad0187bb5676112fe2b1b725e8c2` |
| [`morphogenesis/experiments/E02c_replication/randmask_du3000_d065.json`](../morphogenesis/experiments/E02c_replication/randmask_du3000_d065.json) | other | 2573 | `3b5d19457a338804b8c985b2795f46a144d8fb4ca1e3c02d2dfdaa71a05e7bb3` |
| [`morphogenesis/experiments/E02c_replication/randmask_fp32a_d035.json`](../morphogenesis/experiments/E02c_replication/randmask_fp32a_d035.json) | other | 2544 | `f56a60e8800d72aac9f91c223d646dae5f442756d83cae39962820c9a86834a6` |
| [`morphogenesis/experiments/E02c_replication/randmask_fp32a_d065.json`](../morphogenesis/experiments/E02c_replication/randmask_fp32a_d065.json) | other | 2505 | `6d8944c0b3d266a0afa277ba6d36f9cde3cd934d6fd755dedf021994f929077a` |
| [`morphogenesis/experiments/E02c_replication/randmask_s101_2000_d020.json`](../morphogenesis/experiments/E02c_replication/randmask_s101_2000_d020.json) | other | 2284 | `b903970116dbfd0f0c9c8c186e864e64940cb2db70fa61d1b1c500aa7f470e8e` |
| [`morphogenesis/experiments/E02c_replication/randmask_s101_2000_d050.json`](../morphogenesis/experiments/E02c_replication/randmask_s101_2000_d050.json) | other | 2291 | `740ddf2e17b7e50da24fed8e7c88194ebee06db7cbbaef28a8c7fc343b5ad496` |
| [`morphogenesis/experiments/E02c_replication/randmask_s101_2000_d080.json`](../morphogenesis/experiments/E02c_replication/randmask_s101_2000_d080.json) | other | 2282 | `7b5bf4bc14f5d5372ffd61224102186cc97a8cc770a0cf503ef8a0ca178ec1f7` |
| [`morphogenesis/experiments/E02c_replication/randmask_sp202_d035.json`](../morphogenesis/experiments/E02c_replication/randmask_sp202_d035.json) | other | 2592 | `73f76898f503d5d3a0bd80f59db7136cb9c94929e7445d1ba4738b88ac43d85a` |
| [`morphogenesis/experiments/E02c_replication/randmask_sp202_d065.json`](../morphogenesis/experiments/E02c_replication/randmask_sp202_d065.json) | other | 2581 | `dad30ffddd57576aff49d8401f2520979bb99131fab96334d017e2ce8e3e77ab` |
| [`morphogenesis/experiments/E02c_replication/seed_grid.json`](../morphogenesis/experiments/E02c_replication/seed_grid.json) | derived | 6731 | `8ed405953086a5e5186ef2561c3c08bb4c7bf4a3994ac1097929685667881fdb` |
| [`morphogenesis/experiments/E02c_replication/seed_grid_failures.json`](../morphogenesis/experiments/E02c_replication/seed_grid_failures.json) | derived | 1907 | `6fcfd6fabb274f17e980b338ee93611ec1072751babeb1735be0c79592855473` |
| [`morphogenesis/experiments/E02c_replication/signature_curve.json`](../morphogenesis/experiments/E02c_replication/signature_curve.json) | other | 4847 | `89e90593c25d833cf59ec818af417ac4720c8b8207255b11a425b2b8387841cc` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32long_3000.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32long_3000.json) | derived | 2978 | `6310b773f1130205a1fdd5496013bbfbdfd1c625e9851a5f39a6f9ea57a83c39` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32long_4000.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32long_4000.json) | derived | 2978 | `0aa51cbb645a2682fc582741c6a38af73243dff0893dd3befa640b8111875adb` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_1000.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_1000.json) | derived | 3303 | `effb3abf745b88f18f40c8c5d8201de30001c8205a0de7e4484605ee08a0ad69` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_2000.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_2000.json) | derived | 3303 | `0722b569de22c428a1e678d3d55cb9df0f375226d45b48d79f7a01e2e048dc82` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_3000.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_3000.json) | derived | 3303 | `8465cc6b9dfafdbd16a26d08a771f6c43e12e234070c5d563724ac5cc20159be` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_500.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_500.json) | derived | 3302 | `f7255422f35a3ccdc7346dfc495d73d65a8b574ab64496195639f5a95e6593c4` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c.json`](../morphogenesis/experiments/E02c_replication/summary_e02c.json) | derived | 2604 | `c7fadd291f5ae5775a803c02f92ecf317181c4f3433f6a8e64f1892e050abacb` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_data404.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_data404.json) | derived | 2471 | `f30dd008c0790ff7bef157bad07eca4379d527acb48c23036cfa308767f2dce3` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_s4000.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_s4000.json) | derived | 2485 | `1d8a465f4eb63170c0cc44c7e4b74a631f8d061a7c713c735cfbbd0d3d900003` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed101.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed101.json) | derived | 2904 | `b3624e6f994f1dbfd21caa1fa4a6904c114b115ba42e7c601ccead83f1961ee8` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed202.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed202.json) | derived | 2908 | `6faa9475e943433b34150ec43c716612f1804b8866caf9591ed25de72a206603` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed42.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed42.json) | derived | 2498 | `c2efa823ac5578e9a43fa4f2e479101a304042fa20131132d32f237062bcf073` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed42_tf32on.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed42_tf32on.json) | derived | 2498 | `ef35be7d29a06a563c48a02cb2496b02d062e3f01febafc550d2d11ef4e2a1a1` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_randinit.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_randinit.json) | derived | 2507 | `8b7554a2c27487829e12d78ef70c9a2848a7966707db030bd923d6155987044d` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_scan_seed101.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_scan_seed101.json) | derived | 3313 | `8043ab5a2cbfc0d6d59df64f27a01de31c808d4d8bb9746ecc0d858872de8f0d` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_seed42repro.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_seed42repro.json) | derived | 1510 | `75d6be9db986b7af0634ed7ab5da89d3081e1774914163aca6ac71d74a21f308` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_seed42repro_frozen.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_seed42repro_frozen.json) | derived | 2435 | `aa3c171f6eb992500a56c5cf0b8e0ee542057ac1d40a9c4587063e686c5aa78c` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_A.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_A.json) | derived | 2400 | `a41ba7a2920b00bb53ce88170799480e84623d291197bd1c1ceb5106ed23be83` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_B.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_B.json) | derived | 2414 | `17eceb360983b3e9935859e3cb0d34f5a4f9da0621f0881521ae43e4f1aee3b8` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_wave2.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_wave2.json) | derived | 4097 | `2ff023ca77097129de058418ad328e1d1e426559715ccdb70fc4b402b9e9989e` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_tf32_s4000.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_tf32_s4000.json) | derived | 2471 | `42be9b10e7d29f07a888f1089492697e457c4febd11a8e64a651537eb7e904f7` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_transient.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_transient.json) | derived | 3759 | `2401c70f3dcfa04ffbddc09b044b940ba035dd09906a68cf67280ac985e4638a` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_transient_fp32.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_transient_fp32.json) | derived | 3763 | `c22a8a32ddf6253316c3c1a15a7ca7012dbcaa9319606eb8ac7035e4df3cc1d2` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_transient_seed101.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_transient_seed101.json) | derived | 3778 | `23035f859a4455710b7a4f92466e3259c467936088cc9a7ad3bf8a6f73e76087` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_transient_seed202.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_transient_seed202.json) | derived | 3805 | `e06e9c750008bb52499b2b491abdfe2da10d9860a4417577c607421e93d1a5ba` |
| [`morphogenesis/experiments/E02c_replication/topology_by_family.json`](../morphogenesis/experiments/E02c_replication/topology_by_family.json) | other | 5614 | `a187321b5956f1d8c270c1c8ffcfe89856fe9693985e34b840a89bb6b5e793dd` |
| [`morphogenesis/experiments/E09_pond/adequacy/ghost_control.json`](../morphogenesis/experiments/E09_pond/adequacy/ghost_control.json) | other | 1394 | `f042f0068598ec664fa323c4c4ae76ad589a475aadb97dcb6e81dc6efbf86549` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_cheap_s171.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_cheap_s171.json) | other | 191228 | `e942f35652a2d68380c0f6200977941160ea745c2a7dd4194584faecb7c9ea53` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_cheap_s172.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_cheap_s172.json) | other | 191102 | `b9367876b1d151ce89c8307adac18318838254eb045e97f6b3071926784b663d` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_cheap_s173.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_cheap_s173.json) | other | 190391 | `5950e0859a6e20bb285b5d883acfdb385402ed79b707d469df38d029fbcf4e8e` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_cheap_s174.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_cheap_s174.json) | other | 191114 | `c8e75df1b80bf441911628ac7c48bac24d78b88fd1569cd98f9c49cf4c2bdb65` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_cheap_s175.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_cheap_s175.json) | other | 190880 | `b703addfd373999628e506012262d8301263f1a311f517882d2ac3a434f94d93` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_cost_s171.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_cost_s171.json) | other | 191303 | `c9ccc6f8808762abda0d850214dd2b4707f0f9b8ff0cacaa6e335ca7d5e4215c` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_cost_s172.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_cost_s172.json) | other | 191557 | `d1946f156eb289bd458b8277ac757600a30f6dbcf62d753c52b5907d0fa77093` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_cost_s173.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_cost_s173.json) | other | 190981 | `23f154392ef1a8c32ad50b5f6af6541c4530a020aee35126ba8943cfcdfbf0e7` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_cost_s174.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_cost_s174.json) | other | 191087 | `eb4f265b3c1a6e8bdfb5be882b3d79aed3ea4d0f5bb16e48406badea9de8f6d4` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_cost_s175.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_cost_s175.json) | other | 191119 | `b16de6157b7be4fe5d9b62d574a135b1d38cfecf307ba6e927f60db7ef8157ea` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_free_s171.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_free_s171.json) | other | 191534 | `3df60c4397857d9b9968c59e8dd6c481354d2dc167638a4aebc30d302ea5a15d` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_free_s172.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_free_s172.json) | other | 191275 | `f1674082f1a2ab3698ba15e257d5c6e2d1a0e2fc0457ce2c92777900c975eb7f` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_free_s173.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_free_s173.json) | other | 190698 | `725b6d5b588cf7504a00a282077aa60e6b58ef3f5b149674204923f394d585a1` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_free_s174.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_free_s174.json) | other | 191054 | `6ed4c622a6bee32393fd9699e546ba09ba061c61674fa68b05b1e7b00f1407d0` |
| [`morphogenesis/experiments/E09_pond/adequacy/x44_free_s175.json`](../morphogenesis/experiments/E09_pond/adequacy/x44_free_s175.json) | other | 191408 | `4e79608e6ded38b360f128de6f5f91c3b9370ac5b5819edce832025ee9730e50` |
| [`morphogenesis/experiments/E09_pond/adequacy_matrix.json`](../morphogenesis/experiments/E09_pond/adequacy_matrix.json) | other | 4029 | `4152c79f6c26bbbac2d454760bdd5f22d957ae57f63d1da7057c861c606b66ff` |
| [`morphogenesis/experiments/E09_pond/adequacy_mi.json`](../morphogenesis/experiments/E09_pond/adequacy_mi.json) | other | 5546 | `b7b85ce201b333d407927abafd6b8f7c778a3b5153b344073f8ce5aed1c20c27` |
| [`morphogenesis/experiments/E09_pond/analysis/ci_p_invasion_dose5.json`](../morphogenesis/experiments/E09_pond/analysis/ci_p_invasion_dose5.json) | other | 580 | `d0619878aec45ee4bccd3a19a4b1155f8fcdacc8de203dc756b4e0747b00f22c` |
| [`morphogenesis/experiments/E09_pond/analysis/ci_p_invasion_keep_patches.json`](../morphogenesis/experiments/E09_pond/analysis/ci_p_invasion_keep_patches.json) | other | 734 | `9f93fb5afd872ad0be466f4c2fca567e9870fe72d3d62e3fb7c21b14340dc012` |
| [`morphogenesis/experiments/E09_pond/analysis/ci_p_invasion_keep_uniform.json`](../morphogenesis/experiments/E09_pond/analysis/ci_p_invasion_keep_uniform.json) | other | 536 | `3d38ee6d16b8ab789b159c02a37aea95dc6bcfb49afcbe1f0aa7c30dd3503ecf` |
| [`morphogenesis/experiments/E09_pond/analysis/ci_p_invasion_majority.json`](../morphogenesis/experiments/E09_pond/analysis/ci_p_invasion_majority.json) | other | 704 | `ca32fc1c8b4cb89145dbcc4639627c85462dc2f51476d8998dbe42a7778942c6` |
| [`morphogenesis/experiments/E09_pond/analysis/ci_p_pair_any_tag.json`](../morphogenesis/experiments/E09_pond/analysis/ci_p_pair_any_tag.json) | other | 624 | `9530e275b2f544a2b60e897f990fef33d7aa5a02f49d859b2f4bbd2da7b7923d` |
| [`morphogenesis/experiments/E09_pond/analysis/ci_p_pair_same_tag.json`](../morphogenesis/experiments/E09_pond/analysis/ci_p_pair_same_tag.json) | other | 611 | `633cc91131fbcc4184ad80fb755258c6d201dff822dd5cb0c33ac4e40a20a0e5` |
| [`morphogenesis/experiments/E09_pond/analysis/ci_p_selection_replication.json`](../morphogenesis/experiments/E09_pond/analysis/ci_p_selection_replication.json) | other | 605 | `6987eeb116b0e1433e47a41e8fffa560a9e2384afdd91d4ec5c24beeb2ac2055` |
| [`morphogenesis/experiments/E09_pond/analysis/power_lines_price.json`](../morphogenesis/experiments/E09_pond/analysis/power_lines_price.json) | other | 1770 | `a0596d75c0c6f65fd70e644549c43905d285cb6bd9bdbf4678026c2023563ae5` |
| [`morphogenesis/experiments/E09_pond/analysis/provenance-legacy.json`](../morphogenesis/experiments/E09_pond/analysis/provenance-legacy.json) | other | 1408 | `68bd278d6bc94b866d5ced3d6afdc443ad4c1071beb368267f758b30dc44ebac` |
| [`morphogenesis/experiments/E09_pond/analysis/recompute_i_onebud.json`](../morphogenesis/experiments/E09_pond/analysis/recompute_i_onebud.json) | other | 722 | `079be6b5fc5272db4d9b8dee649b91d3b7c6469161055147f8e50cf16de8f6ce` |
| [`morphogenesis/experiments/E09_pond/analysis/recompute_i_pairany.json`](../morphogenesis/experiments/E09_pond/analysis/recompute_i_pairany.json) | other | 742 | `7aec2ec210a02d41e84f509c070bfd2cf7032239fd65efd58d2643e7046d0e81` |
| [`morphogenesis/experiments/E09_pond/analysis/recompute_i_w2bud3.json`](../morphogenesis/experiments/E09_pond/analysis/recompute_i_w2bud3.json) | other | 720 | `282df9503d1f9aedbd8b5cf6963f222ff9559147b69ee1e327eadf7b55d92c81` |
| [`morphogenesis/experiments/E09_pond/analysis/recompute_i_w2budd2.json`](../morphogenesis/experiments/E09_pond/analysis/recompute_i_w2budd2.json) | other | 686 | `932d65da63d296317e24cea83540dabcaf48d708cc05caaed56d5c5eafc5015b` |
| [`morphogenesis/experiments/E09_pond/analysis/response_independent.json`](../morphogenesis/experiments/E09_pond/analysis/response_independent.json) | other | 2283 | `ac96df05b42151acba34032328c1af7676011a213ca181863baf58d61d78c480` |
| [`morphogenesis/experiments/E09_pond/analysis/whale_w2bud3.json`](../morphogenesis/experiments/E09_pond/analysis/whale_w2bud3.json) | other | 2673 | `57de9e830a283498567bee0b2d9150e437456b832c9c2b1033539ae9dbe6c1fd` |
| [`morphogenesis/experiments/E09_pond/b2_matrix.json`](../morphogenesis/experiments/E09_pond/b2_matrix.json) | other | 5544 | `78430a53f06bfbc0b1f6270daf188265d338c6a751eed7562bb6372d26b6d986` |
| [`morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed1.json`](../morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed1.json) | other | 130063 | `fdb73048896daf327bfe5cc79b99715dc90c807907ce6ecd4a9ff32a1d38769c` |
| [`morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed2.json`](../morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed2.json) | other | 129542 | `b33a7aef273f8a8f72dfc8c51352712b1704bf1e9fc6b6a5e685df8720d890e4` |
| [`morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed3.json`](../morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed3.json) | other | 128661 | `3853a8f8b485d5e0806b9c9c2d62f8589782fb7c84aa49f626560173912747d8` |
| [`morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed1.json`](../morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed1.json) | other | 129809 | `4e6bd23ee40f104b99e9922fef854a1ae620bc0a99e31fa7d0ad8ec2fa6d3420` |
| [`morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed2.json`](../morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed2.json) | other | 129940 | `b9f221a47094bf927d52a07de791d772cd498afa7023e4db64d2f65110b4a297` |
| [`morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed3.json`](../morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed3.json) | other | 129646 | `d427c1ab26e33b14dda2d89812820aa58ad18ae59fd7bcc234755ba73e815b14` |
| [`morphogenesis/experiments/E09_pond/catastrophe_diversity.json`](../morphogenesis/experiments/E09_pond/catastrophe_diversity.json) | other | 23620 | `38aa7dcc80f46d1540bac554ba6e546459dcc3c74e9d1dd8c1c500c0c6bed50b` |
| [`morphogenesis/experiments/E09_pond/catastrophe_matrix.json`](../morphogenesis/experiments/E09_pond/catastrophe_matrix.json) | other | 24427 | `003a762db45d64d6965b22d32578e2f610589e65fde96510ff1d8750c907d715` |
| [`morphogenesis/experiments/E09_pond/coexistence_matrix.json`](../morphogenesis/experiments/E09_pond/coexistence_matrix.json) | other | 35122 | `1bfce70d26c9fe60db479877c30f43bc21fa456b7a86a2d2f83f3593c07598df` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_inherit_seed1.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_inherit_seed1.json) | other | 130075 | `c6aff913a4e1c8923b5ca37dcbf3c53a5953c1f9d0607dff78dbb286a3665803` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_inherit_seed2.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_inherit_seed2.json) | other | 130160 | `66be6c3e14caa110fa4745bff26e2da23a9668cf5946a233ba8a068d9c18acb7` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_inherit_seed3.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_inherit_seed3.json) | other | 129835 | `c8385d1db11818e526a85faec9ce0cc51ce80146c34abeec8dc5035e56f0c3b8` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_random_seed1.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_random_seed1.json) | other | 130496 | `011379dfccabccaf5a27c69220372128a9de31be29ce79d138bb2d2b30dd9bff` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_random_seed2.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_random_seed2.json) | other | 130652 | `ae61aba54297db2a5e9570708827fd9c5cacacf1190d630d08a8bdc06239ade6` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_random_seed3.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_AinvB_random_seed3.json) | other | 130198 | `d2257cb0f847392a9426c3274400e13425ec9eb6790a8fb53b86d1cf62d7817b` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_inherit_seed1.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_inherit_seed1.json) | other | 126789 | `15c32890d43e367b493a3e0573758c822e3e7bfa9f404834b41afb4fa420e069` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_inherit_seed2.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_inherit_seed2.json) | other | 126833 | `b91aa90b66c9b44d5ce7532fc51f5a1371be5167369e8df54433b2e7378cefe3` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_inherit_seed3.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_inherit_seed3.json) | other | 127086 | `116bdeea18e5243ce224388906de5f7ced20cab9b112a1bc9244774465c187fe` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_random_seed1.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_random_seed1.json) | other | 128869 | `1865e4180de7a64b75d4749f8d0d80e0cef83ae331baa9407e7ae243d6068091` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_random_seed2.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_random_seed2.json) | other | 129198 | `4090fb2b0cb0e657759ea1cb92671e98e758efda04b22b90384dc571ba3e2801` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_random_seed3.json`](../morphogenesis/experiments/E09_pond/colinv3_fd0_BinvA_random_seed3.json) | other | 128428 | `1794499bb4055f457599b0513a58c7ddaabf8c84cc0b29e2a4835eae1f161407` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_inherit_seed1.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_inherit_seed1.json) | other | 130163 | `e8b7ef446425fe4eb4b3f90f3ce1a5c548ba054fabddb59df61f1843fca7afe7` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_inherit_seed2.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_inherit_seed2.json) | other | 129880 | `3c1be38aa1ed47dd0d71381a066dfc70777da6479f2bb79e437bc952d08ed03c` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_inherit_seed3.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_inherit_seed3.json) | other | 129499 | `2574a2d57b56dc190f35b3383c43ae37d5468045444c2705046646cb3d755974` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_random_seed1.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_random_seed1.json) | other | 130577 | `218da2316376c460cad62f64908b8ce4ea9cd9d5cdff8fc3fdcfb12127d697d1` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_random_seed2.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_random_seed2.json) | other | 130342 | `2514a302d815c9395fd1bcaff7a400756ff67ced6f99d9382819d31f61d69de6` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_random_seed3.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_AinvB_random_seed3.json) | other | 129949 | `deaa04c2e2390b8d90eda34afdfc98765dcdf7c464108cb6b441dc51f111e7c9` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_inherit_seed1.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_inherit_seed1.json) | other | 127262 | `503a5e995d7dadf2d31b9730fdf7725ba765bf46f88c6c4329fe838996f64c40` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_inherit_seed2.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_inherit_seed2.json) | other | 126772 | `eb43e5bde67d094acdc35c34dc1f889cd9098a556bd74182ec525ca75b87c5b1` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_inherit_seed3.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_inherit_seed3.json) | other | 127009 | `0d44e5661196aeafc964bc0ff29038797761ce2af4d6f08cc111fcf1ec7581be` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_random_seed1.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_random_seed1.json) | other | 128851 | `841a3832824bf4b3e764c80fee7b7a9ba77f37fc4ff0c15e534b617680f3ef8e` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_random_seed2.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_random_seed2.json) | other | 128968 | `81d65aec77c7ef291467a46f5a874207ce4557a6dfd6810ed9e489cfc748a08e` |
| [`morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_random_seed3.json`](../morphogenesis/experiments/E09_pond/colinv3_fd10_BinvA_random_seed3.json) | other | 128623 | `7a2798ce8f932bd5b8681b905fd1da1630014db303a2b37e33e998016b748ea0` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed1.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed1.json) | other | 167097 | `962589d5ea8d75b322a44dbd1c2b856fd44a4718e98dcd4c70c9dd12b1737686` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed10.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed10.json) | other | 166627 | `f4a37dd1166de24fce8f61346d1082f51be25bb7bfe96940deb8eacd08e99a86` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed2.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed2.json) | other | 166830 | `881bfdbb71fd4561b50684b8f590c9920016264a2ea364fab87c81ea09c73adf` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed3.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed3.json) | other | 166370 | `865501ec6b830136dd7cc8332c1671e2d5ec6e9c0993d50c728c0c3b45efe037` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed4.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed4.json) | other | 167089 | `282440db119838dd6e087cae2bc3f66744c170a00decc65b48ea938cdba9340e` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed5.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed5.json) | other | 166703 | `ced2118d2f27fa3b75016f6b0e881a951924f56bd9f0b33cae24eb6b80b01d05` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed6.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed6.json) | other | 166932 | `c30496f668a4169086e8d43cc8c5dd487bf6c8942ed66858d305cc57902f124d` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed7.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed7.json) | other | 166965 | `9b7b221afcd81ec380fde382cdec50284deebf4095bcf718528b672177a8d4a1` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed8.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed8.json) | other | 166552 | `c353d92a8dd58be0b0765eca4da629e68503837ba263ee2fc0492a93ee8e8acf` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed9.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n10_seed9.json) | other | 166494 | `48654f7fb88f7b4b36c6244421d7cad382c1de47deb40d789b6aec7a02ee2407` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed1.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed1.json) | other | 167096 | `2bb45ad531503a8476fabe08705698f404087c37a0cb1a228d7f7b9b40c73319` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed10.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed10.json) | other | 166692 | `a6506ae2c5bd98ce565a420c1e4e041ce2fbc1de610be9c76c5d783c899dcfc3` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed2.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed2.json) | other | 166834 | `1cf3bbb485c4e385d35c4b8fbe01dcf3879570380724e3c0b067fad5e74f490d` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed3.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed3.json) | other | 166400 | `a73f8303c3a6050fa8e69eb1993f46549ef0e44e58efb32bf33f366e8902a02b` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed4.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed4.json) | other | 167091 | `572db2c05eeac2d4a3188931b55f138efe9bcf5f32b64261a8a5dd9db5cc7b6b` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed5.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed5.json) | other | 166615 | `e3c175cb5c92b9122c3346dc602b409ad0dabeea3bbc3583a00bb97765a3551d` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed6.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed6.json) | other | 166940 | `496dbe6f69dc0dd78f6645615d63b33836bc4bca5327456cd9fd6e0a3034ded0` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed7.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed7.json) | other | 167066 | `3625b229b53a163d0c544fbf7385c05f6acde4b90a1b389a425fc6f510ba05df` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed8.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed8.json) | other | 166589 | `6aadb918e4ffabe16c4a9833b855b72b3e1d5da99c5c98e33ebd4d7bc028cac5` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed9.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n1_seed9.json) | other | 166492 | `8e70465af7d66ace31acab255bf358a87d28a7de82bbb1b483aa56c9c1a2ae9b` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed1.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed1.json) | other | 167013 | `9c6d9cc467111fea521749a2d3767d5e11964375faad64667574090fea6766df` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed10.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed10.json) | other | 166696 | `8e86590915292cdf52458868c5b8be0da36a5651d30abb8819faab76131fabfd` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed2.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed2.json) | other | 166873 | `6b1c33a38ab2df88f66fa58a6d6b6282aee149123e5f1cbf725fdf0d922254b6` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed3.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed3.json) | other | 166522 | `0266eca80df174b39d9e03f50e25af782c36fd6a371aef48147fd335bb84149c` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed4.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed4.json) | other | 167089 | `1e98e36c799a7b71799d7438190cb153e74bda4b7ea7b9c7e8b4a1d62e80ca0a` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed5.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed5.json) | other | 166633 | `0babc79a4885f5fdba0770a9df97e3673fb2670c92d1a46ee6c3bcbc8f88901d` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed6.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed6.json) | other | 166932 | `59060c70c8199b91b6414f226fe7d0df55caad77fa0e9279a3bb69d47024d421` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed7.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed7.json) | other | 166965 | `bc5cd6c4c77ca6aca87b844684e0f7b5c8ea3fcf2e50b76c83013428f268738c` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed8.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed8.json) | other | 166552 | `ffb0fd356cdb753d200d3662fb95dc48ccb364d28579fa307aada23dade9b82b` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed9.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n20_seed9.json) | other | 166494 | `f63cff01f34ee7f699037b9f758276ae7480b2e595bd42a17cc16ad6e37e6b10` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed1.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed1.json) | other | 167076 | `bdf6d105f12d2d9a7c65daae9edfed3952d399a7b1c7af5699a1824db7bb6c40` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed10.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed10.json) | other | 166684 | `79982e13a95ccc43fe86cfbdc826b9417e3162332a69e4316dcdf86da19bd296` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed2.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed2.json) | other | 166817 | `bc86d09a6ed46d2540899a9b0b84cfc6cbf0175af975630ef2d1df8ae363a8ef` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed3.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed3.json) | other | 166387 | `85ecbecc36120408098475024ac9d3db2cc61e3ad9b6d6cc04a3b9f1565268b6` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed4.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed4.json) | other | 167087 | `4faf03822e4c8f1d80a32ee4029706e9e19d1085d7bd385548bb06faeb5db1fa` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed5.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed5.json) | other | 166513 | `b4d66c49caa5010aec9915a3fc22331b349e7e29e17e2f290210977aa9b9ac19` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed6.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed6.json) | other | 166929 | `ea66b90d8a12b33bd7117010457986cf7db830d631bcb1c6dc9359da3cdaab9c` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed7.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed7.json) | other | 167004 | `79f179ae13d5a4f45e57b5465400323133d1529ac751aa5ee5a106c733fd6e16` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed8.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed8.json) | other | 166326 | `10b09c502aa3831b97e89f3c7e6ebfa6a803853cfaab48210d87097409be6088` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed9.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n2_seed9.json) | other | 166492 | `3274d7001a84c3590de503eea16bedce423114afe56a7339335474727759f2b0` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed1.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed1.json) | other | 166989 | `2006a716c559e64d1e9d8a282fdb9f2a1cc5af35ecaa3436035e80cca13654fe` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed10.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed10.json) | other | 166684 | `7f0456e759382ddc1b6e85c6631f3c63e036afa2afdfd5a9bc2b0196837507c6` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed2.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed2.json) | other | 166281 | `aed02297dd74642790c2831b365c1d230ff48de72982a419c41c95222d7a4168` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed3.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed3.json) | other | 166446 | `db991d8020b1b449cf0163e1dfce1c0b107828073a7f2ca764cdbfd5c148e121` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed4.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed4.json) | other | 167087 | `980d4a617b75062308e1b296416c5de2e3faec53768f5497098d20bf0c0a72e0` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed5.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed5.json) | other | 166691 | `9a4eb694e0a9299479e023b5e6fecceeb451107e76848178d2d2f16a34568c38` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed6.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed6.json) | other | 166930 | `41cc720a15e082ebe2df8010e036550aff1ce26215f59f61a83a06f1caab5871` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed7.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed7.json) | other | 166944 | `bccf08a912c484b03f8c18c43626b18a9141127990a50229cbff1125d91651ae` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed8.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed8.json) | other | 166550 | `012fbae09ac18568879df62d6b4268dc51f06d996912ce2b2b56de573bf38ecb` |
| [`morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed9.json`](../morphogenesis/experiments/E09_pond/colinv4_fd10_AinvB_inherit_n5_seed9.json) | other | 166492 | `c52235e330b1f219404a80c1c5a9332346b9881c01dfe073d4d18f7d764c0688` |
| [`morphogenesis/experiments/E09_pond/colony_type_matrix.json`](../morphogenesis/experiments/E09_pond/colony_type_matrix.json) | other | 14218 | `6f0e31b4dc3889d2f8257085b5c9369714dbda1f1ce5eb08439adc617be57603` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_base.json`](../morphogenesis/experiments/E09_pond/diag_ignition_base.json) | other | 128332 | `b18a23673e15e8bb455726c9fc8a886995ffc567db0afc3c6e946b786dddfc7f` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_gate.json`](../morphogenesis/experiments/E09_pond/diag_ignition_gate.json) | other | 112669 | `d077adf2a67087d6fd806f28173d637579a8718a47ad206ae9bc20825650fc00` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_nofill.json`](../morphogenesis/experiments/E09_pond/diag_ignition_nofill.json) | other | 126844 | `fd7a22b2d9fea04791a7737f297decc7f0d63e873085693768e3fa5c865f3090` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_noincome.json`](../morphogenesis/experiments/E09_pond/diag_ignition_noincome.json) | other | 117172 | `edf7d2eb084f907d6bde547d73f1c13080c4f2482ee2276d71cf70a255c4b295` |
| [`morphogenesis/experiments/E09_pond/drift_matrix.json`](../morphogenesis/experiments/E09_pond/drift_matrix.json) | other | 6712 | `0a1c9e6d0ad10beddd7f2f2065df3ab77e4a896114d1802802f289227b5369d9` |
| [`morphogenesis/experiments/E09_pond/e2_object_ablation.json`](../morphogenesis/experiments/E09_pond/e2_object_ablation.json) | other | 4252 | `b99a1574e39d9f8be0861fbecdcc52fd00d456c571907e1c1244b592bd6464d9` |
| [`morphogenesis/experiments/E09_pond/e4_sensitivity.json`](../morphogenesis/experiments/E09_pond/e4_sensitivity.json) | other | 5523 | `30fc19ac068261be087d89d574a28c23a83336f1ecae32f3353fb632a132f91f` |
| [`morphogenesis/experiments/E09_pond/found_n10_seed1.json`](../morphogenesis/experiments/E09_pond/found_n10_seed1.json) | other | 162023 | `79c7be6d49a102a9ed8b014fe6fa32a98de2bb12694c3c54d8ff9b15e98968c5` |
| [`morphogenesis/experiments/E09_pond/found_n10_seed10.json`](../morphogenesis/experiments/E09_pond/found_n10_seed10.json) | other | 162707 | `d06b4b349f07b8d34e24f2737700f1f19bb454d6bc778b76f171d05833a98dc0` |
| [`morphogenesis/experiments/E09_pond/found_n10_seed2.json`](../morphogenesis/experiments/E09_pond/found_n10_seed2.json) | other | 162079 | `0b45ef56e6c42a1b6baf475246c5eca17432e2b109931e4f2fcf59cb68830138` |
| [`morphogenesis/experiments/E09_pond/found_n10_seed3.json`](../morphogenesis/experiments/E09_pond/found_n10_seed3.json) | other | 163001 | `7027a3ee12edc702e9ef94443e63702c483326a9cce1ba1cbf4caf7e079f89e8` |
| [`morphogenesis/experiments/E09_pond/found_n10_seed4.json`](../morphogenesis/experiments/E09_pond/found_n10_seed4.json) | other | 162770 | `df0fa6b0a346fc597042e0c4c32e38661f4cf52c228d9d20d8dd45535af9b865` |
| [`morphogenesis/experiments/E09_pond/found_n10_seed5.json`](../morphogenesis/experiments/E09_pond/found_n10_seed5.json) | other | 162509 | `7e7119470a5075342155afd50bedfff9d7da76743844dfe8718df9a2f40a1f08` |
| [`morphogenesis/experiments/E09_pond/found_n10_seed6.json`](../morphogenesis/experiments/E09_pond/found_n10_seed6.json) | other | 162697 | `b0537649ff0f632cfce00a00a13da527efe08cc8b5aa0a29cf52a788894162de` |
| [`morphogenesis/experiments/E09_pond/found_n10_seed7.json`](../morphogenesis/experiments/E09_pond/found_n10_seed7.json) | other | 162538 | `b1b49ffbf41530240a54eaf8fe73761dd3149a7db7925b35aa29afb8e0587b97` |
| [`morphogenesis/experiments/E09_pond/found_n10_seed8.json`](../morphogenesis/experiments/E09_pond/found_n10_seed8.json) | other | 162896 | `475ebeb1a4cb9b36f81a9f7d267003cfe1fd88e4755fc2fdefdf7d690ac459ca` |
| [`morphogenesis/experiments/E09_pond/found_n10_seed9.json`](../morphogenesis/experiments/E09_pond/found_n10_seed9.json) | other | 162922 | `2228b2ad78b11f91ac5c42cbe5cdbc468356ab26bcd89871dd1179f832e1bbe9` |
| [`morphogenesis/experiments/E09_pond/found_n1_seed1.json`](../morphogenesis/experiments/E09_pond/found_n1_seed1.json) | other | 161514 | `b0a45eba950017a1b635d2fb0c2e8c39aa56dd1e836786d46776f1553f0bc8d5` |
| [`morphogenesis/experiments/E09_pond/found_n1_seed10.json`](../morphogenesis/experiments/E09_pond/found_n1_seed10.json) | other | 161692 | `c01eca9fb2567faeff2060b9366c1ca24567e345578b1a26beae774d94642205` |
| [`morphogenesis/experiments/E09_pond/found_n1_seed2.json`](../morphogenesis/experiments/E09_pond/found_n1_seed2.json) | other | 161493 | `d16ac51cb3ad2f64a7be7f9f8a7e2979f74a783fc85f8c29704ffbe7fe6a2fe9` |
| [`morphogenesis/experiments/E09_pond/found_n1_seed3.json`](../morphogenesis/experiments/E09_pond/found_n1_seed3.json) | other | 161947 | `51adac273df7a055b918365353c6aed8f24480f78d15ffc6c317c7d4870cd451` |
| [`morphogenesis/experiments/E09_pond/found_n1_seed4.json`](../morphogenesis/experiments/E09_pond/found_n1_seed4.json) | other | 161755 | `aca064b43f68816e738af8c791f6e034925c506c132715f3130c669abcaeed00` |
| [`morphogenesis/experiments/E09_pond/found_n1_seed5.json`](../morphogenesis/experiments/E09_pond/found_n1_seed5.json) | other | 160699 | `ac134aa38ec0cfb4390deea10d910b4ca49e3a1b180214a7bf7bd4613a29a972` |
| [`morphogenesis/experiments/E09_pond/found_n1_seed6.json`](../morphogenesis/experiments/E09_pond/found_n1_seed6.json) | other | 161826 | `427f7f32d5e51af0f7e948c705743dddc86cdfd9d7aad39c20159aff866a19d1` |
| [`morphogenesis/experiments/E09_pond/found_n1_seed7.json`](../morphogenesis/experiments/E09_pond/found_n1_seed7.json) | other | 161744 | `522182813c43745c8d4d42d3e9be800fb3147968187f3ee1c4edd1b57d8bdb38` |
| [`morphogenesis/experiments/E09_pond/found_n1_seed8.json`](../morphogenesis/experiments/E09_pond/found_n1_seed8.json) | other | 161395 | `ba899a24e22c67a50ead79460581295f3a874b5d4fa0ae0fe68a9aa59b31b4a7` |
| [`morphogenesis/experiments/E09_pond/found_n1_seed9.json`](../morphogenesis/experiments/E09_pond/found_n1_seed9.json) | other | 161711 | `9068a208122765e56cb32e3b2875c4e6b6c14bd9a40233a23fd6e89dafdf23b8` |
| [`morphogenesis/experiments/E09_pond/found_n20_seed1.json`](../morphogenesis/experiments/E09_pond/found_n20_seed1.json) | other | 162870 | `f87a720486bf55de8b2ed82807ec924aeb86a0230d5b2e20e0a55ca3c04e8f5d` |
| [`morphogenesis/experiments/E09_pond/found_n20_seed10.json`](../morphogenesis/experiments/E09_pond/found_n20_seed10.json) | other | 163316 | `2ce8bac7b0791945dd50f4b6d97e2ad52723014fa56fba95008709de26c49e02` |
| [`morphogenesis/experiments/E09_pond/found_n20_seed2.json`](../morphogenesis/experiments/E09_pond/found_n20_seed2.json) | other | 163209 | `f210174eff838c86cbd3a077fce1d778d62c25153bda4a52dbd7581f881178f5` |
| [`morphogenesis/experiments/E09_pond/found_n20_seed3.json`](../morphogenesis/experiments/E09_pond/found_n20_seed3.json) | other | 163396 | `8b46ffb566ecdf38d171f5214039212cb82973c9dc487cd3e2a487f884a79d75` |
| [`morphogenesis/experiments/E09_pond/found_n20_seed4.json`](../morphogenesis/experiments/E09_pond/found_n20_seed4.json) | other | 163484 | `a6c02ab138352e7cdef9d2940ebe8600929dabb557db840a92c5f49031f8fe03` |
| [`morphogenesis/experiments/E09_pond/found_n20_seed5.json`](../morphogenesis/experiments/E09_pond/found_n20_seed5.json) | other | 163075 | `d73ed2831b513c061cfd062559cd0059e0bdd992c67d7743e9cd2317a75c12ff` |
| [`morphogenesis/experiments/E09_pond/found_n20_seed6.json`](../morphogenesis/experiments/E09_pond/found_n20_seed6.json) | other | 163432 | `eecdf7b7d4b182cbb4bfde4bcca56fcab70956d9b59b68762e56423c9634e2d4` |
| [`morphogenesis/experiments/E09_pond/found_n20_seed7.json`](../morphogenesis/experiments/E09_pond/found_n20_seed7.json) | other | 163462 | `c2654bfbaf31be5c726d7931e593f3ef6aea006bb3f8cc420231bbffbc667a27` |
| [`morphogenesis/experiments/E09_pond/found_n20_seed8.json`](../morphogenesis/experiments/E09_pond/found_n20_seed8.json) | other | 163638 | `f7ce0a0821a1feb998dbb87c3870672d138e951664848cf88d33ceb031314199` |
| [`morphogenesis/experiments/E09_pond/found_n20_seed9.json`](../morphogenesis/experiments/E09_pond/found_n20_seed9.json) | other | 163570 | `a27b26ffb86ddc9c4b8dbdda28df1ea8694d557db9365027d61982f579a36c03` |
| [`morphogenesis/experiments/E09_pond/found_n2_seed1.json`](../morphogenesis/experiments/E09_pond/found_n2_seed1.json) | other | 161393 | `f4e5fc9cd97fa601cb14835301ceb326e931fad085a141d23098c11f59b7b11c` |
| [`morphogenesis/experiments/E09_pond/found_n2_seed10.json`](../morphogenesis/experiments/E09_pond/found_n2_seed10.json) | other | 161254 | `a3f01bf003a090472dbb7d3f601eb09c83c00ef20ee97b55829e5a19eebbc057` |
| [`morphogenesis/experiments/E09_pond/found_n2_seed2.json`](../morphogenesis/experiments/E09_pond/found_n2_seed2.json) | other | 161067 | `b2dc354890282e10c681c95e3734f3dffd0fc3150f8e7c9a17a754fa16edc637` |
| [`morphogenesis/experiments/E09_pond/found_n2_seed3.json`](../morphogenesis/experiments/E09_pond/found_n2_seed3.json) | other | 161991 | `db8696e4d1bfe0bb4aad7abcccbcd71e3600902e900c8fab658018c0162a818a` |
| [`morphogenesis/experiments/E09_pond/found_n2_seed4.json`](../morphogenesis/experiments/E09_pond/found_n2_seed4.json) | other | 160921 | `a2b1fee5d5212ec31939051343c1cd64fef699aff6aeaf038cea9bf33e1d9ff9` |
| [`morphogenesis/experiments/E09_pond/found_n2_seed5.json`](../morphogenesis/experiments/E09_pond/found_n2_seed5.json) | other | 160522 | `aabb45a9898a622f38017f48dea6d77694e1cdf4e08208ed3f5abe86afbc842b` |
| [`morphogenesis/experiments/E09_pond/found_n2_seed6.json`](../morphogenesis/experiments/E09_pond/found_n2_seed6.json) | other | 162003 | `e14532733b1f89f38971c64bcef7564fe6e17b15b5f19bdaecabaf43cc27ac75` |
| [`morphogenesis/experiments/E09_pond/found_n2_seed7.json`](../morphogenesis/experiments/E09_pond/found_n2_seed7.json) | other | 160995 | `6bdbaeeddbc8c2cc398da80480f7040d91f3cb2f41937c020db5f75ed37e3074` |
| [`morphogenesis/experiments/E09_pond/found_n2_seed8.json`](../morphogenesis/experiments/E09_pond/found_n2_seed8.json) | other | 161424 | `d72f62d688c3c26e7f117e33fc72f9faea380914c0a43f280788c8c690cf85e5` |
| [`morphogenesis/experiments/E09_pond/found_n2_seed9.json`](../morphogenesis/experiments/E09_pond/found_n2_seed9.json) | other | 161190 | `78c762565f3070f28deabdb3bdd031bf4aacf49ccd981df59cacba7d206d6a00` |
| [`morphogenesis/experiments/E09_pond/found_n5_seed1.json`](../morphogenesis/experiments/E09_pond/found_n5_seed1.json) | other | 161140 | `9e7c8802a5fdb32edcacdf2b88019268128bc21530ce798c01f7286d04e0707e` |
| [`morphogenesis/experiments/E09_pond/found_n5_seed10.json`](../morphogenesis/experiments/E09_pond/found_n5_seed10.json) | other | 162037 | `a0fb29c0294054093d256fc5454ab694447ba4556293a080d345fd4c8702dd99` |
| [`morphogenesis/experiments/E09_pond/found_n5_seed2.json`](../morphogenesis/experiments/E09_pond/found_n5_seed2.json) | other | 162391 | `e46d4b8167c168f8b4f595cb3b5667ca788059f015e3c7906a60b84332fe98bf` |
| [`morphogenesis/experiments/E09_pond/found_n5_seed3.json`](../morphogenesis/experiments/E09_pond/found_n5_seed3.json) | other | 162538 | `423565000c64e10577e3ccad3e76fe85dc9ed717954662392bbaf2fa9296f94f` |
| [`morphogenesis/experiments/E09_pond/found_n5_seed4.json`](../morphogenesis/experiments/E09_pond/found_n5_seed4.json) | other | 162467 | `3a61e6ed550dabfe56e31838095512f9fbe806287cd134ead1d12e6aa15a2162` |
| [`morphogenesis/experiments/E09_pond/found_n5_seed5.json`](../morphogenesis/experiments/E09_pond/found_n5_seed5.json) | other | 161931 | `d737b7677ef61be4e0f3b7c3ae1d5ac0f6389a00c4cc108b78e6c1fab258b4b9` |
| [`morphogenesis/experiments/E09_pond/found_n5_seed6.json`](../morphogenesis/experiments/E09_pond/found_n5_seed6.json) | other | 161710 | `54aea16a8afc5aded2086b7a4c60ea58f0b4fe93ad9d68b8089ce7d38ec41f3a` |
| [`morphogenesis/experiments/E09_pond/found_n5_seed7.json`](../morphogenesis/experiments/E09_pond/found_n5_seed7.json) | other | 161931 | `57404d6db93f8f4f3f2e17124a9b24e5d42568d390f29a0c4de76aac7d15df82` |
| [`morphogenesis/experiments/E09_pond/found_n5_seed8.json`](../morphogenesis/experiments/E09_pond/found_n5_seed8.json) | other | 162764 | `29bd393faff6c0198d75c4c4aac6b3cd42aef4624aed55af1380ad1e47aeec31` |
| [`morphogenesis/experiments/E09_pond/found_n5_seed9.json`](../morphogenesis/experiments/E09_pond/found_n5_seed9.json) | other | 162656 | `07d18cc51a2164d3e1f311f0a51e838db55bd9664b988693b707d287710de799` |
| [`morphogenesis/experiments/E09_pond/founding_maps.json`](../morphogenesis/experiments/E09_pond/founding_maps.json) | other | 13570 | `e7db4369162b9718713856e6f2ad4b5401659250584db4afc73fbc9b0b109472` |
| [`morphogenesis/experiments/E09_pond/founding_matrix.json`](../morphogenesis/experiments/E09_pond/founding_matrix.json) | other | 28855 | `8edce560f3113c423bac1b023edf184c70324134300d51632f2e6ff69f350060` |
| [`morphogenesis/experiments/E09_pond/frequency_matrix.json`](../morphogenesis/experiments/E09_pond/frequency_matrix.json) | other | 19352 | `5ca8e3fe20e4e098e3cb5d5d94c363c28aaf5c73ab02412b7d71fab553962d82` |
| [`morphogenesis/experiments/E09_pond/frequency_matrix_v2.json`](../morphogenesis/experiments/E09_pond/frequency_matrix_v2.json) | other | 24234 | `689782d2fcb7ebb828eade5c2fdb9d985459296b0c343ae22efc11a5cff3c092` |
| [`morphogenesis/experiments/E09_pond/frequency_start_control.json`](../morphogenesis/experiments/E09_pond/frequency_start_control.json) | other | 6007 | `8a09a2a49002ca3378f27d7259f93814097ab52bdfda7644e05cbf77a1841159` |
| [`morphogenesis/experiments/E09_pond/generation_matrix.json`](../morphogenesis/experiments/E09_pond/generation_matrix.json) | other | 7060 | `2398e6b51516e1286830063f7c430ae5cf08d442d12416a99b7205090e423210` |
| [`morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed1.json`](../morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed1.json) | other | 166248 | `4332cbf28f616fd9a787324265ba12c1ee6a692b5f8766b1f2cba13aaf21522b` |
| [`morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed2.json`](../morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed2.json) | other | 166809 | `62a42401e58d28f81451663bd7cb41c38e1daab2a542afb6ebbd355f49769244` |
| [`morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed3.json`](../morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed3.json) | other | 166373 | `b2369ace72c1c8802b4a59836010075c14547f5a4694b4599bde62904a50a09c` |
| [`morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed1.json`](../morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed1.json) | other | 148518 | `aa8b5802025697e5830e5a565a9403d7913bda1f22996884a662e7354cbc45aa` |
| [`morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed2.json`](../morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed2.json) | other | 166554 | `b1bba692ea109bd58893cc079fe93baa83adc4d05091e86c12482202097b31fc` |
| [`morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed3.json`](../morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed3.json) | other | 166601 | `1cdd19757875dc2f96013741597c4be46322a282db78ce00536013f41ce11d9d` |
| [`morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed1.json`](../morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed1.json) | other | 166101 | `374c196bd2e6418d4cb2842a3f2baf419b1d8e329c60ce05e5d0057615380dc4` |
| [`morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed2.json`](../morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed2.json) | other | 166639 | `16bfd2960b7f63ea0a45d9b3d14b41abc3afa9572ed00230af0bc26816d16796` |
| [`morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed3.json`](../morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed3.json) | other | 166227 | `3876ffbfa5fe5a28a177966e5a5cdd6827551f973d043f120db17ea71f466e29` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_ghost_s171.json`](../morphogenesis/experiments/E09_pond/ghost/x50_ghost_s171.json) | other | 172510 | `870d0cb64017e0b52bccd5a6149912d9504e17c1f946c71cdb1ef56d6dc16866` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_ghost_s172.json`](../morphogenesis/experiments/E09_pond/ghost/x50_ghost_s172.json) | other | 172604 | `c118155bc247f5041473dc4986890bc88b03dc2c447b1798d2bb026cb77ab840` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_ghost_s173.json`](../morphogenesis/experiments/E09_pond/ghost/x50_ghost_s173.json) | other | 172232 | `55da5ecf0b38988cd3e9c17ce33d100cc0ddd0b6a6e1f2cc964ca266efc73b89` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_ghost_s174.json`](../morphogenesis/experiments/E09_pond/ghost/x50_ghost_s174.json) | other | 172401 | `f64d92155501d5310a332ab5ac07428036b64c253ecfe4cc556a23685ba35171` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_ghost_s175.json`](../morphogenesis/experiments/E09_pond/ghost/x50_ghost_s175.json) | other | 172163 | `afedba1d56ee36b89eb863ebe9ff1718f2747dfab7f5dfd6454abdadab5aca6e` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_ghost_s176.json`](../morphogenesis/experiments/E09_pond/ghost/x50_ghost_s176.json) | other | 172598 | `300bed463da6cce0f26a3afa607ab768a50050d6571308ee57d356084fc2a17d` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_ghost_s177.json`](../morphogenesis/experiments/E09_pond/ghost/x50_ghost_s177.json) | other | 172201 | `1e1f5a2baf85b6cd105ac36df5ea62d430e67f5bef9ae349eb02c14e156e708b` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_ghost_s178.json`](../morphogenesis/experiments/E09_pond/ghost/x50_ghost_s178.json) | other | 172201 | `fc59cd38ef7bb43d02c0fd95689c5e5634bd089d0f9e1808f682676bb79d68c8` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_normal_s171.json`](../morphogenesis/experiments/E09_pond/ghost/x50_normal_s171.json) | other | 191303 | `c9ccc6f8808762abda0d850214dd2b4707f0f9b8ff0cacaa6e335ca7d5e4215c` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_normal_s172.json`](../morphogenesis/experiments/E09_pond/ghost/x50_normal_s172.json) | other | 191557 | `d1946f156eb289bd458b8277ac757600a30f6dbcf62d753c52b5907d0fa77093` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_normal_s173.json`](../morphogenesis/experiments/E09_pond/ghost/x50_normal_s173.json) | other | 190981 | `23f154392ef1a8c32ad50b5f6af6541c4530a020aee35126ba8943cfcdfbf0e7` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_normal_s174.json`](../morphogenesis/experiments/E09_pond/ghost/x50_normal_s174.json) | other | 191087 | `eb4f265b3c1a6e8bdfb5be882b3d79aed3ea4d0f5bb16e48406badea9de8f6d4` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_normal_s175.json`](../morphogenesis/experiments/E09_pond/ghost/x50_normal_s175.json) | other | 191119 | `b16de6157b7be4fe5d9b62d574a135b1d38cfecf307ba6e927f60db7ef8157ea` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_normal_s176.json`](../morphogenesis/experiments/E09_pond/ghost/x50_normal_s176.json) | other | 191401 | `ba2f9296bc3430daab29dd2181af7b3c7e425fd4490724309c69a5b3979bd74f` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_normal_s177.json`](../morphogenesis/experiments/E09_pond/ghost/x50_normal_s177.json) | other | 191009 | `dc83b6f09e838a801e07ee6a42de33a41a1632e6c01b2a31e12cdf083535d97e` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_normal_s178.json`](../morphogenesis/experiments/E09_pond/ghost/x50_normal_s178.json) | other | 190947 | `731ef1e39bfcb5258b8d50b576365c94e114e12fcbf58eab8a224983f251be57` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_normal_s179.json`](../morphogenesis/experiments/E09_pond/ghost/x50_normal_s179.json) | other | 191701 | `5efbf52bc4defc7cde3b207f4e77495ab1cc946037f94d5a9d621e5d6c372c76` |
| [`morphogenesis/experiments/E09_pond/ghost/x50_normal_s180.json`](../morphogenesis/experiments/E09_pond/ghost/x50_normal_s180.json) | other | 191243 | `89d4453e2a933048ee18729373937373fb754c7d230e65f76e673c91199f4573` |
| [`morphogenesis/experiments/E09_pond/ghost_matrix.json`](../morphogenesis/experiments/E09_pond/ghost_matrix.json) | other | 1396 | `31f9e0843832468a2cc6dcc14a1a66208e0b0cc99a5ec83427d9d209ed02e335` |
| [`morphogenesis/experiments/E09_pond/habitable/x43_hab_s171.json`](../morphogenesis/experiments/E09_pond/habitable/x43_hab_s171.json) | other | 414678 | `ca335f88f5c7484fe7ded2105d828abcc2eba482f28ac396bf47ae942d49b8be` |
| [`morphogenesis/experiments/E09_pond/habitable/x43_hab_s172.json`](../morphogenesis/experiments/E09_pond/habitable/x43_hab_s172.json) | other | 414903 | `6b64f9d4fa5d0239347a901d8a09d4a79707e83ba4a7e0cb2fc5a2949468d836` |
| [`morphogenesis/experiments/E09_pond/habitable/x43_hab_s173.json`](../morphogenesis/experiments/E09_pond/habitable/x43_hab_s173.json) | other | 414427 | `020ba0c228918d51f77ef2cf793911a655dcc1c72e65541f41d6d02318cbacb3` |
| [`morphogenesis/experiments/E09_pond/habitable/x43_hab_s174.json`](../morphogenesis/experiments/E09_pond/habitable/x43_hab_s174.json) | other | 414493 | `dee12991c3c1bb64ad4455382fd6e904fa597234e438f259b6c49315dc2a8dca` |
| [`morphogenesis/experiments/E09_pond/habitable/x43_hab_s175.json`](../morphogenesis/experiments/E09_pond/habitable/x43_hab_s175.json) | other | 414550 | `974a77aed40ac31b1417c3ae49670b0c1f5e1e7d59cbe4eb1939b6064a65c145` |
| [`morphogenesis/experiments/E09_pond/habitable/x43_hab_s176.json`](../morphogenesis/experiments/E09_pond/habitable/x43_hab_s176.json) | other | 414817 | `14275b528641738f21347d052fe4ffc23255d2b0d5f33461988126a4c80755e9` |
| [`morphogenesis/experiments/E09_pond/habitable/x43_hab_s177.json`](../morphogenesis/experiments/E09_pond/habitable/x43_hab_s177.json) | other | 414404 | `8ee81c12a380d2c1087931be10b88664dba64819b2def064b2866463c7b1d982` |
| [`morphogenesis/experiments/E09_pond/habitable/x43_hab_s178.json`](../morphogenesis/experiments/E09_pond/habitable/x43_hab_s178.json) | other | 414357 | `f11e57787b3f801a33eeca3c40ffe0b7dbc6e7c3464727fe7048b12df72bc24e` |
| [`morphogenesis/experiments/E09_pond/habitable/x43_hab_s179.json`](../morphogenesis/experiments/E09_pond/habitable/x43_hab_s179.json) | other | 415088 | `0dd2235aebfa02bb061791bfa74409cfad57c8f4e98668aa5dafe463f4d434e1` |
| [`morphogenesis/experiments/E09_pond/habitable/x43_hab_s180.json`](../morphogenesis/experiments/E09_pond/habitable/x43_hab_s180.json) | other | 414595 | `d1c215e869c8611aa59f99eabf59cea8284df20f486b8b43b97a6e6684f5237f` |
| [`morphogenesis/experiments/E09_pond/habitable_matrix.json`](../morphogenesis/experiments/E09_pond/habitable_matrix.json) | other | 3000 | `9c9a58759752795e45c46830669921a318c3e0f77c8c53d5ee3101dfc44c989f` |
| [`morphogenesis/experiments/E09_pond/inherit2_gradflip_fixed.json`](../morphogenesis/experiments/E09_pond/inherit2_gradflip_fixed.json) | other | 1564 | `7afabe8f08591035e95c5d57244e52ee7f4a9b4d4ec5dbd931800df4afb2f798` |
| [`morphogenesis/experiments/E09_pond/inherit2_patches_fixed.json`](../morphogenesis/experiments/E09_pond/inherit2_patches_fixed.json) | other | 1562 | `0da84ca1f69206c8da5a6721c8604202226904ddf92156b6c6b38d96d118638a` |
| [`morphogenesis/experiments/E09_pond/inherit2_uniform_fixed.json`](../morphogenesis/experiments/E09_pond/inherit2_uniform_fixed.json) | other | 1566 | `24d8e5a2da7b7cf772655a83594c1c34553f05d3a478b92f779c20b2bc388295` |
| [`morphogenesis/experiments/E09_pond/invader_death_matrix.json`](../morphogenesis/experiments/E09_pond/invader_death_matrix.json) | other | 13215 | `8825b9898a545a86f611dff8c1a0ad9e60dd532ceeaa57fd9908c7cbad506a94` |
| [`morphogenesis/experiments/E09_pond/invader_dose_matrix.json`](../morphogenesis/experiments/E09_pond/invader_dose_matrix.json) | other | 37696 | `0c89416985acdda18556a3653291298aec6a56288b6f4cd2025f4ccfe6775380` |
| [`morphogenesis/experiments/E09_pond/invasion_matrix.json`](../morphogenesis/experiments/E09_pond/invasion_matrix.json) | other | 6771 | `9054d63e0a3693d2791a75cf32c4264654461fb0ff861de67b85ad77f5ee2e46` |
| [`morphogenesis/experiments/E09_pond/invasion_state_probe.json`](../morphogenesis/experiments/E09_pond/invasion_state_probe.json) | other | 1072 | `2916417e786b974c7a8993e1ca3fe6a28be36ffe47cdbd53dfa8a5dcbbb7fb37` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed1.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed1.json) | other | 170182 | `d3fbf07afc30b2d75ee6987e307867887d4372ecf286b8c80fa2c2d4844bd642` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed10.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed10.json) | other | 169836 | `1c2faf636385970cace3dd4779e3fc9ecde44715be86aec5262bbec605a0449e` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed2.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed2.json) | other | 169718 | `63ead37ee405c6f3ccf20ba1b142aae47c4b6964b212c96ed62f89d54fb6f2c5` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed3.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed3.json) | other | 169662 | `0d6e9eb9e9d1c9728495e9e33077e9ad8b1888b598a8164b9ee68992e14f0641` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed4.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed4.json) | other | 169810 | `ecce7837dd45bcc2dacfa885ab6b2f5c168f3c5546abfc56368817c6467d283f` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed5.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed5.json) | other | 169927 | `b98b001fcd947f89dd80e50f4c0d1618c106140263f10e879a3f73118baf741b` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed6.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed6.json) | other | 169640 | `db775cefdf905f933131eb4a2b91def5a69ece0eea6a04c83bea78a148d478e4` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed7.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed7.json) | other | 169790 | `9381bb2735cec5e531f6a6df7152bd04359b57013132dbd6749c4ddfbc229656` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed8.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed8.json) | other | 169427 | `7a4e021541759ea140905abb6b661b6f7ccbd13b1f04ad100261d54a7e4b1851` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed9.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_keep_seed9.json) | other | 169198 | `4851eed1b1f46674aa5e24e90817894b7e6c1755be73c883d5c621d8ca504792` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed1.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed1.json) | other | 169721 | `4d6dc5a4f38ae24f019c6fadb4e3388673709ed61c5032c4e27b3449a23b40fb` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed10.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed10.json) | other | 169401 | `c761e72d0a8dfcf365d88148ffdc3ddbaf57be4d2676af9154b7d7f423b0834d` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed2.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed2.json) | other | 169582 | `797cc1e92fd1e2e031c8af3a68579be4ec907edf3d1a044ce50ef4c3f0106d0e` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed3.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed3.json) | other | 169230 | `f9c720ec1f46d19d69f77f12aab04e16ad995791ac5333cd47aabff196e48a48` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed4.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed4.json) | other | 169797 | `5b18c091855033d0883eb33ce22505c723e18a066e828b42cc9817fb8e83b372` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed5.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed5.json) | other | 169341 | `deb3ee1c54be985afb510dfc99cae55713e439e4975686001993bd681405d1cf` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed6.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed6.json) | other | 169640 | `9dad60f64b60559470c3dbbfa7b4b03813f1a0fbb3fb3c15e4d60d84c8e1799c` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed7.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed7.json) | other | 169673 | `ea1321c224fdc63c9d71497e2e5134e583284c42b4d71bd5f1c024c435896d3c` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed8.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed8.json) | other | 169261 | `1a71d6ed94fa400a790691ae2979619566db8a6f2b2e79ec7d1a517f48451ec7` |
| [`morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed9.json`](../morphogenesis/experiments/E09_pond/invdeath/invdeath_majority_seed9.json) | other | 169198 | `ac4d8772c26a0d04b3bbabd4e545fd94b159fb3eb2c84ca0e0dd370bbcf47af2` |
| [`morphogenesis/experiments/E09_pond/kill_keep2_matrix.json`](../morphogenesis/experiments/E09_pond/kill_keep2_matrix.json) | other | 7538 | `5c26319de25570585cd98378c3d222522b5a5ce0d04ab0f940ab1e012f65fac2` |
| [`morphogenesis/experiments/E09_pond/kill_keep3_matrix.json`](../morphogenesis/experiments/E09_pond/kill_keep3_matrix.json) | other | 7540 | `288159588354260eb100445f892599fd9b6878d8321f548219cda7ccce2d4287` |
| [`morphogenesis/experiments/E09_pond/kill_keep_matrix.json`](../morphogenesis/experiments/E09_pond/kill_keep_matrix.json) | other | 6262 | `276661ecc78cba1d3996c406ca13d084755d10b104a359563ba25f80f61e0db4` |
| [`morphogenesis/experiments/E09_pond/killkeep2_clean_seed1.json`](../morphogenesis/experiments/E09_pond/killkeep2_clean_seed1.json) | other | 473 | `69d374ba0c9c78abda08a00120ae16880c13e6b45d3619fa0dd1b3f1f627c16e` |
| [`morphogenesis/experiments/E09_pond/killkeep2_clean_seed2.json`](../morphogenesis/experiments/E09_pond/killkeep2_clean_seed2.json) | other | 472 | `e2dc0df68cd4dce6919baa5a0f5163a635b0ab6ad740a08481595ad444d2ef9e` |
| [`morphogenesis/experiments/E09_pond/killkeep2_clean_seed3.json`](../morphogenesis/experiments/E09_pond/killkeep2_clean_seed3.json) | other | 473 | `bd082482e0dd43c4a9f22e0a2bee6bd4b4f8ab61228337717f07bb467faf0d63` |
| [`morphogenesis/experiments/E09_pond/killkeep2_clean_seed4.json`](../morphogenesis/experiments/E09_pond/killkeep2_clean_seed4.json) | other | 473 | `c2f2d62b51f91cf410cb63d2ccb5094d929bd573e2f369e025cc79e4520cd9b3` |
| [`morphogenesis/experiments/E09_pond/killkeep2_clean_seed5.json`](../morphogenesis/experiments/E09_pond/killkeep2_clean_seed5.json) | other | 473 | `6274975e5a552ad149b0b71d10b5c33f481e2a609410ec94dbdf67bbcb650514` |
| [`morphogenesis/experiments/E09_pond/killkeep2_keep_seed1.json`](../morphogenesis/experiments/E09_pond/killkeep2_keep_seed1.json) | other | 475 | `93fea34a4fcb9cde53ae0254e4520cbb51ca976f7b5aa1f5a502f4ff39e9555d` |
| [`morphogenesis/experiments/E09_pond/killkeep2_keep_seed2.json`](../morphogenesis/experiments/E09_pond/killkeep2_keep_seed2.json) | other | 473 | `aa9652a3fa784e1ef9d4e0f3562ebf2f6c809f1846295447346d82dc692e3f4d` |
| [`morphogenesis/experiments/E09_pond/killkeep2_keep_seed3.json`](../morphogenesis/experiments/E09_pond/killkeep2_keep_seed3.json) | other | 475 | `d6a224e0b132dc8442cfa7a549cac79a96c71c7e343b6690afac0ba0766f8fde` |
| [`morphogenesis/experiments/E09_pond/killkeep2_keep_seed4.json`](../morphogenesis/experiments/E09_pond/killkeep2_keep_seed4.json) | other | 475 | `94bbfd931df5bb0e7ab565384e6303cfd491a7e7546c3f9a70c29de608b8588b` |
| [`morphogenesis/experiments/E09_pond/killkeep2_keep_seed5.json`](../morphogenesis/experiments/E09_pond/killkeep2_keep_seed5.json) | other | 475 | `7d265da7d756c264a5b48cb4cb768cc3aa8536b5720176082ef82dde1668028f` |
| [`morphogenesis/experiments/E09_pond/killkeep3_clean_seed1.json`](../morphogenesis/experiments/E09_pond/killkeep3_clean_seed1.json) | other | 473 | `55e6393a3acf94e8cf2b504d654d31b3a3516617cf53c4e00a035faa58aedd9c` |
| [`morphogenesis/experiments/E09_pond/killkeep3_clean_seed2.json`](../morphogenesis/experiments/E09_pond/killkeep3_clean_seed2.json) | other | 473 | `1673ec0d5c95e38e792846194eaeeab0e5cf59fa1ee14500c41ac201364a3dcd` |
| [`morphogenesis/experiments/E09_pond/killkeep3_clean_seed3.json`](../morphogenesis/experiments/E09_pond/killkeep3_clean_seed3.json) | other | 473 | `19288b250c7ae06e5b2e4be27ad8e9c962ffd0cc011bf4d55b42c01ab44ae3fd` |
| [`morphogenesis/experiments/E09_pond/killkeep3_clean_seed4.json`](../morphogenesis/experiments/E09_pond/killkeep3_clean_seed4.json) | other | 473 | `1b2bad542ab6aa2764d31e6acc8f4b96ef2da9c855a79eb4c346e1cf2981db41` |
| [`morphogenesis/experiments/E09_pond/killkeep3_clean_seed5.json`](../morphogenesis/experiments/E09_pond/killkeep3_clean_seed5.json) | other | 473 | `1b5099517bff4516f4279f71aa7642acea3f2271efd4ad12d2dbbdfcaa95c341` |
| [`morphogenesis/experiments/E09_pond/killkeep3_keep_seed1.json`](../morphogenesis/experiments/E09_pond/killkeep3_keep_seed1.json) | other | 475 | `b7ffca6885c786aa88e3deff8b29c0d3d73e6b3088bcd9862cc771a728fa69f5` |
| [`morphogenesis/experiments/E09_pond/killkeep3_keep_seed2.json`](../morphogenesis/experiments/E09_pond/killkeep3_keep_seed2.json) | other | 475 | `13c18d05bad235f3c8b6f36f10127435daa4888262e59c6f065354f9faa26f89` |
| [`morphogenesis/experiments/E09_pond/killkeep3_keep_seed3.json`](../morphogenesis/experiments/E09_pond/killkeep3_keep_seed3.json) | other | 475 | `c2ace04af42f1864fb8f64049e1072f63454f0e4cbfbc3e46f8a9e3aa360fd48` |
| [`morphogenesis/experiments/E09_pond/killkeep3_keep_seed4.json`](../morphogenesis/experiments/E09_pond/killkeep3_keep_seed4.json) | other | 475 | `4aba2f0c87dbb5972c487ea9e47bfcd6904984bf89471ad6a605a6bdcfe33cff` |
| [`morphogenesis/experiments/E09_pond/killkeep3_keep_seed5.json`](../morphogenesis/experiments/E09_pond/killkeep3_keep_seed5.json) | other | 475 | `5d08ee5b5324643db1fddc5d42a573e3912c11f573ff461c126cc44592cb55f9` |
| [`morphogenesis/experiments/E09_pond/killkeep_clean_seed1.json`](../morphogenesis/experiments/E09_pond/killkeep_clean_seed1.json) | other | 353 | `12430451d32527f1351f48a8389375d83f5c18dcb59bc4b8c0a45e1924a1d16a` |
| [`morphogenesis/experiments/E09_pond/killkeep_clean_seed2.json`](../morphogenesis/experiments/E09_pond/killkeep_clean_seed2.json) | other | 353 | `48ae562b03b7e26311bec2578027175ffde7734ed7a1cc8408cc9601ca315359` |
| [`morphogenesis/experiments/E09_pond/killkeep_clean_seed3.json`](../morphogenesis/experiments/E09_pond/killkeep_clean_seed3.json) | other | 352 | `a816699845306d738f2f4448191ff324d44d9f5ca56439d991007ac364ff78bb` |
| [`morphogenesis/experiments/E09_pond/killkeep_clean_seed4.json`](../morphogenesis/experiments/E09_pond/killkeep_clean_seed4.json) | other | 353 | `ec5bd6cecc9bd55e36fe0614bea86e54f724516fa26c61f5949b75fbff2352b8` |
| [`morphogenesis/experiments/E09_pond/killkeep_clean_seed5.json`](../morphogenesis/experiments/E09_pond/killkeep_clean_seed5.json) | other | 354 | `55365a1ad63907fa2a5db8e355178ab573a05d85881a9892341f6067453ccbdd` |
| [`morphogenesis/experiments/E09_pond/killkeep_keep_seed1.json`](../morphogenesis/experiments/E09_pond/killkeep_keep_seed1.json) | other | 355 | `1e5206b9e232ae19468e451d90f3b1de92232644af1e8297359baf1e86bd4038` |
| [`morphogenesis/experiments/E09_pond/killkeep_keep_seed2.json`](../morphogenesis/experiments/E09_pond/killkeep_keep_seed2.json) | other | 354 | `30c820f3de502666e1cab4a8be65b7fb0a40a5617e6f60e041601922ad549e41` |
| [`morphogenesis/experiments/E09_pond/killkeep_keep_seed3.json`](../morphogenesis/experiments/E09_pond/killkeep_keep_seed3.json) | other | 354 | `47dcc19a07e743e35fa67abbbabcfe66006244b2c3f80efe9110ce55b0c555b1` |
| [`morphogenesis/experiments/E09_pond/killkeep_keep_seed4.json`](../morphogenesis/experiments/E09_pond/killkeep_keep_seed4.json) | other | 355 | `a9277b156ae7360f00618ce8bab89c1bfe164841cadabdb702c3712440c758bc` |
| [`morphogenesis/experiments/E09_pond/killkeep_keep_seed5.json`](../morphogenesis/experiments/E09_pond/killkeep_keep_seed5.json) | other | 356 | `71bbe1a92f43ba013d06e56dfd5c3d84723b45d6a4c29ca1749f8e2ce5e3fd6a` |
| [`morphogenesis/experiments/E09_pond/l1_field_betti.json`](../morphogenesis/experiments/E09_pond/l1_field_betti.json) | other | 40127 | `01fd1420abc18d016c85645b20a0938a8d5abfc0eb89868389a12a2549c40c4a` |
| [`morphogenesis/experiments/E09_pond/l1_field_cadence.json`](../morphogenesis/experiments/E09_pond/l1_field_cadence.json) | other | 10062 | `422f91d575cf55db1b652e2f837e29deda39af3fb602d905f0d52bf6d92aacd5` |
| [`morphogenesis/experiments/E09_pond/l1_field_e6p_selection.json`](../morphogenesis/experiments/E09_pond/l1_field_e6p_selection.json) | other | 1998 | `a55068fe1da88d38855e202c568aae1f3f82b6a662e304117f0034c07328db2c` |
| [`morphogenesis/experiments/E09_pond/l1_field_e6q_niches.json`](../morphogenesis/experiments/E09_pond/l1_field_e6q_niches.json) | other | 2017 | `951045202682dfdd4a9a6c5f6fcdf9df5a29e52b1203f69ea9e2c005eaac0e02` |
| [`morphogenesis/experiments/E09_pond/l1_field_size_resolved.json`](../morphogenesis/experiments/E09_pond/l1_field_size_resolved.json) | other | 8667 | `43e00057d8e3c52a43e672539cd698ebb8d1c15bb42001cdcc1401daf53d7cec` |
| [`morphogenesis/experiments/E09_pond/l1_field_stationarity.json`](../morphogenesis/experiments/E09_pond/l1_field_stationarity.json) | other | 3118 | `4baf2a1d3ca407ec12d08f6fe0ab199d4873024f8c5050af3acbf11878b8a25c` |
| [`morphogenesis/experiments/E09_pond/l1_field_x100_cutfree.json`](../morphogenesis/experiments/E09_pond/l1_field_x100_cutfree.json) | other | 1844 | `c36d2544bb6fbc765e1fc7c16376c2fd2317cdc70e5b7052c74216d7deeecc3c` |
| [`morphogenesis/experiments/E09_pond/l1_field_x101_watershed.json`](../morphogenesis/experiments/E09_pond/l1_field_x101_watershed.json) | other | 1599 | `07d8417c3d383f10d66b27153bfd7f5b73d696e6f0e0e538b70713a0a24a5381` |
| [`morphogenesis/experiments/E09_pond/l1_field_x101b_dense.json`](../morphogenesis/experiments/E09_pond/l1_field_x101b_dense.json) | other | 1659 | `e72f2a95aff3ebfe6883ed0bf20d1ee85b4ead92deef651c0d80f374a9f1153b` |
| [`morphogenesis/experiments/E09_pond/l1_field_x102_specificity_ladder.json`](../morphogenesis/experiments/E09_pond/l1_field_x102_specificity_ladder.json) | other | 1716 | `90147b0272a5e47c0da8de4ad7abd76f9a83a61bc831041b4b2e49f06bc2c9d2` |
| [`morphogenesis/experiments/E09_pond/l1_field_x102b_dense.json`](../morphogenesis/experiments/E09_pond/l1_field_x102b_dense.json) | other | 1777 | `0b510f09464170b19ae13104c668a386c835032c187e2ffbe140e94342355a0e` |
| [`morphogenesis/experiments/E09_pond/l1_field_x103_basin_position.json`](../morphogenesis/experiments/E09_pond/l1_field_x103_basin_position.json) | other | 1582 | `115f0d1bd3eca799e8e63f624ed404145116a505d6232a3882a3547c15ae55c4` |
| [`morphogenesis/experiments/E09_pond/l1_field_x103b_basin_position.json`](../morphogenesis/experiments/E09_pond/l1_field_x103b_basin_position.json) | other | 1906 | `44beefa2aedca8f733a01058ec57b9aed0ec64547094e7788e378df12e37f931` |
| [`morphogenesis/experiments/E09_pond/l1_field_x103c_birth_distance.json`](../morphogenesis/experiments/E09_pond/l1_field_x103c_birth_distance.json) | other | 4039 | `98a73d6b432033d5b229fe1ad12bd021316451c549b9178fe716739e14ef13b9` |
| [`morphogenesis/experiments/E09_pond/l1_field_x103d_peak_null.json`](../morphogenesis/experiments/E09_pond/l1_field_x103d_peak_null.json) | other | 4717 | `b6a6797d6a627151b30ecd7891e57236510ede853a4fdaf06b96df9c601223e1` |
| [`morphogenesis/experiments/E09_pond/l1_field_x105_dense.json`](../morphogenesis/experiments/E09_pond/l1_field_x105_dense.json) | other | 4799 | `ed3069e12c6043a2f7e22edb789d743ad7d13e71c12c98d2dd97e8447951f3f2` |
| [`morphogenesis/experiments/E09_pond/l1_field_x106_crowding.json`](../morphogenesis/experiments/E09_pond/l1_field_x106_crowding.json) | other | 3885 | `2cb43bdae8a02b1f6c01940e602ee90ea11a7f3297716de92205d3d7f6a449eb` |
| [`morphogenesis/experiments/E09_pond/l1_field_x107_shared_room.json`](../morphogenesis/experiments/E09_pond/l1_field_x107_shared_room.json) | other | 1372 | `2be1dba1b1dca409354ab42785059d292e8d5b3eb7849f2f6a30dc66d9f02ebd` |
| [`morphogenesis/experiments/E09_pond/l1_field_x109_room_dense.json`](../morphogenesis/experiments/E09_pond/l1_field_x109_room_dense.json) | other | 1370 | `f75f31197f332f9e2207f97553ef53a36a4905a564fb0d2fa654f115fce3d9a1` |
| [`morphogenesis/experiments/E09_pond/l1_field_x110_gamma_cell.json`](../morphogenesis/experiments/E09_pond/l1_field_x110_gamma_cell.json) | other | 2101 | `a4ad2fbcbc0eccbc33c78d41bad61f019c7f8657c5cc66ba36b0ee29790a631c` |
| [`morphogenesis/experiments/E09_pond/l1_field_x110b_gamma_cell.json`](../morphogenesis/experiments/E09_pond/l1_field_x110b_gamma_cell.json) | other | 4769 | `ee6db22d04fdbba7577d8dcc3a68e71c09a69537136243708d3ada83c3b5cd11` |
| [`morphogenesis/experiments/E09_pond/l1_field_x111b_area_lifetime.json`](../morphogenesis/experiments/E09_pond/l1_field_x111b_area_lifetime.json) | other | 2224 | `079ca15934e0f831006124514d7775d040ddd513bdf01476693186f14a61d4ee` |
| [`morphogenesis/experiments/E09_pond/l1_field_x112b_cuts.json`](../morphogenesis/experiments/E09_pond/l1_field_x112b_cuts.json) | other | 1079 | `6ce60a8d89cf5e06cd7d43a773e8ad3fdfaceae53d28fa17b2ccdb9a1452b895` |
| [`morphogenesis/experiments/E09_pond/l1_field_x112c_cuts_maze.json`](../morphogenesis/experiments/E09_pond/l1_field_x112c_cuts_maze.json) | other | 1089 | `640f751a7314a92ac458d87b5b7091cad6c4edd0bf7932876964b77d918afdc4` |
| [`morphogenesis/experiments/E09_pond/l1_field_x113_depth.json`](../morphogenesis/experiments/E09_pond/l1_field_x113_depth.json) | other | 1135 | `72636b7c83dfdf40fded15d0b8adddd7694aaf48294e2660ff45fc535e7680f9` |
| [`morphogenesis/experiments/E09_pond/l1_field_x113b_depth_rate.json`](../morphogenesis/experiments/E09_pond/l1_field_x113b_depth_rate.json) | other | 1359 | `e95ca20c6dab40f02977b300c94bdf9bdd515cd44c6da4cb59d2e6640ff04af6` |
| [`morphogenesis/experiments/E09_pond/l1_field_x113c_depth_rate.json`](../morphogenesis/experiments/E09_pond/l1_field_x113c_depth_rate.json) | other | 1432 | `17578a968d9006ad49debb23b6ac9d685702a6730798d984440c7c10ca744b13` |
| [`morphogenesis/experiments/E09_pond/l1_field_x114_window.json`](../morphogenesis/experiments/E09_pond/l1_field_x114_window.json) | other | 1237 | `54bf02813836b8b3b58e168d963e8c01d2de5f66504c4c2e806dd664617c3001` |
| [`morphogenesis/experiments/E09_pond/l1_field_x115_persistence.json`](../morphogenesis/experiments/E09_pond/l1_field_x115_persistence.json) | other | 1391 | `371b36a0f0175c9ddf296f81d02b53a7bc1a223761c62fea3c714485bd3d7cca` |
| [`morphogenesis/experiments/E09_pond/l1_field_x116_matched.json`](../morphogenesis/experiments/E09_pond/l1_field_x116_matched.json) | other | 1342 | `ef1d52baa36302c85f046fb20fca2d084d7791cd47bdea93220169aba2467892` |
| [`morphogenesis/experiments/E09_pond/l1_field_x117_area_matched.json`](../morphogenesis/experiments/E09_pond/l1_field_x117_area_matched.json) | other | 1486 | `07d1af50479fc6b7580e0e02f708130429a8841a2befbd3a6265ad8352d7a047` |
| [`morphogenesis/experiments/E09_pond/l1_field_x118_mediator.json`](../morphogenesis/experiments/E09_pond/l1_field_x118_mediator.json) | other | 1340 | `7cbdbf21d6200847670aef24f0e474d14869486de17fbf7d0ea9104230373c7b` |
| [`morphogenesis/experiments/E09_pond/l1_field_x119_model.json`](../morphogenesis/experiments/E09_pond/l1_field_x119_model.json) | other | 1103 | `0d1f5f24c017b2e51bbd92164fec45009250995f442c199da2a1486b03da646c` |
| [`morphogenesis/experiments/E09_pond/l1_field_x120_window_daughters.json`](../morphogenesis/experiments/E09_pond/l1_field_x120_window_daughters.json) | other | 1365 | `80d24075042048f0ad721b011e8f65df0026a6a1983eb2c9d0dead444914787a` |
| [`morphogenesis/experiments/E09_pond/l1_field_x121_hazard.json`](../morphogenesis/experiments/E09_pond/l1_field_x121_hazard.json) | other | 1194 | `0eed6ec582f4f46c2dcdc937ebd3e0464ec222d9ac48b4d7c22a30e7db1cb989` |
| [`morphogenesis/experiments/E09_pond/l1_field_x124_coherence.json`](../morphogenesis/experiments/E09_pond/l1_field_x124_coherence.json) | other | 1383 | `0369240ac1f10d40e0c11f750a262ce3008a1c1c0c46176ad712978a2d7692aa` |
| [`morphogenesis/experiments/E09_pond/l1_field_x125_definitions.json`](../morphogenesis/experiments/E09_pond/l1_field_x125_definitions.json) | other | 1787 | `e689be9d51b846d7907670c4762b5984f6d0d35e485a644216152df76dead171` |
| [`morphogenesis/experiments/E09_pond/l1_field_x125b_statistics.json`](../morphogenesis/experiments/E09_pond/l1_field_x125b_statistics.json) | other | 2362 | `e740cea8ede9b9a2323ddfe5fb8a2f23cfe7cf894f60ef127cb8e2d47da06198` |
| [`morphogenesis/experiments/E09_pond/l1_field_x125c_ties.json`](../morphogenesis/experiments/E09_pond/l1_field_x125c_ties.json) | other | 2339 | `2021d1b40e5715022b25139f24ab8fc5f1dd1dc3762a7ace3b37a372e0ef799d` |
| [`morphogenesis/experiments/E09_pond/l1_field_x126_third_cell.json`](../morphogenesis/experiments/E09_pond/l1_field_x126_third_cell.json) | other | 4571 | `95e805da23ff1986f2c0b1726de7108a1310cb60add8e0b903bf3a3ac89ee0ee` |
| [`morphogenesis/experiments/E09_pond/l1_field_x127_absorption.json`](../morphogenesis/experiments/E09_pond/l1_field_x127_absorption.json) | other | 3797 | `04c629c4942840f7b67c7d48a9a2e16a5f0dc4828232d7eb77b0d07d6756b35b` |
| [`morphogenesis/experiments/E09_pond/l1_field_x128_kinship.json`](../morphogenesis/experiments/E09_pond/l1_field_x128_kinship.json) | other | 3500 | `30b4cf9aa9979ac794f9908ad8b04a4deb56b84c733f68569ffc8e36455ef1ca` |
| [`morphogenesis/experiments/E09_pond/l1_field_x128b_local.json`](../morphogenesis/experiments/E09_pond/l1_field_x128b_local.json) | other | 4218 | `5fb0b9c9f3e877661bac5555b976159c03dffeb1657c17d9eb5fb6e539fca4cc` |
| [`morphogenesis/experiments/E09_pond/l1_field_x129_geometry.json`](../morphogenesis/experiments/E09_pond/l1_field_x129_geometry.json) | other | 2812 | `9dc87b2805d052ba3ecda4008b63766f78d2a2a8f242d197f7a788aad02cf8c1` |
| [`morphogenesis/experiments/E09_pond/l1_field_x130_remerge.json`](../morphogenesis/experiments/E09_pond/l1_field_x130_remerge.json) | other | 2715 | `3bea47adb80bb37946eda554ae8a14a9e073cd347cf7812c66d240125513a4a8` |
| [`morphogenesis/experiments/E09_pond/l1_field_x131_worlds.json`](../morphogenesis/experiments/E09_pond/l1_field_x131_worlds.json) | other | 38718 | `42494c803c3aea12c7f28ee7cba5b7edce8269484ca02dc0917e1d0bc24f87c4` |
| [`morphogenesis/experiments/E09_pond/l1_field_x132_power.json`](../morphogenesis/experiments/E09_pond/l1_field_x132_power.json) | other | 36478 | `6ce695fa73c0d4d1a9a73ae023e93689f0c304bff1185f5fe8d9234fcf40bc83` |
| [`morphogenesis/experiments/E09_pond/l1_field_x134_mixing.json`](../morphogenesis/experiments/E09_pond/l1_field_x134_mixing.json) | other | 8483 | `cebbb1064d8b705a437fcccd9af716836b6636a3225a359254ad85fb711263e8` |
| [`morphogenesis/experiments/E09_pond/l1_field_x134b_mixing.json`](../morphogenesis/experiments/E09_pond/l1_field_x134b_mixing.json) | other | 4669 | `492a31ec0bdebbabd0b2f628482041e8b1c8c0b7f0b60ceef6364f84f1444a2b` |
| [`morphogenesis/experiments/E09_pond/l1_field_x135_maze_mixing.json`](../morphogenesis/experiments/E09_pond/l1_field_x135_maze_mixing.json) | other | 3130 | `bea99bf5c9fb8f4297c6427b1d859f3427b3915312b2f7e2a271b4969e01c67a` |
| [`morphogenesis/experiments/E09_pond/l1_field_x136_wall.json`](../morphogenesis/experiments/E09_pond/l1_field_x136_wall.json) | other | 8454 | `80f3d1168c5e1e8e21297f1352ac149828e3908893227dc8db8bd5251ba33a9b` |
| [`morphogenesis/experiments/E09_pond/l1_field_x138_scale.json`](../morphogenesis/experiments/E09_pond/l1_field_x138_scale.json) | other | 8482 | `e35f7038793ed32089cedb09b43b67e8e76cb68f30582b1a5e1f2bed2ed88e0f` |
| [`morphogenesis/experiments/E09_pond/l1_field_x139_slowing.json`](../morphogenesis/experiments/E09_pond/l1_field_x139_slowing.json) | other | 9664 | `0b4a53db5cee1f62b2cfad3a0637efeba9f00f4bcc95c7bd692971df2ebe24e4` |
| [`morphogenesis/experiments/E09_pond/l1_field_x140_gap_rule.json`](../morphogenesis/experiments/E09_pond/l1_field_x140_gap_rule.json) | other | 5974 | `d750d5cfdbfd17484a4fe341fab66c5e21e81e4f6934216eef0f9d664212d7c0` |
| [`morphogenesis/experiments/E09_pond/l1_field_x142_coalescence.json`](../morphogenesis/experiments/E09_pond/l1_field_x142_coalescence.json) | other | 61400 | `fcf68e7d6e20a5e1819d6b71dfd54550be45d49486c40917bf48aaaf8f753b02` |
| [`morphogenesis/experiments/E09_pond/l1_field_x145_lone_disc.json`](../morphogenesis/experiments/E09_pond/l1_field_x145_lone_disc.json) | other | 1955 | `2b072fb70af05261b574e06218a9f7cf63d9b1feb6d79647df256c7751a96a28` |
| [`morphogenesis/experiments/E09_pond/l1_field_x147_radius45.json`](../morphogenesis/experiments/E09_pond/l1_field_x147_radius45.json) | other | 8421 | `c05f8d29b67c5611ee0545e50cec0ddb0f126e82b5bee8d6566cc5f58367fb1a` |
| [`morphogenesis/experiments/E09_pond/l1_field_x150_radius6.json`](../morphogenesis/experiments/E09_pond/l1_field_x150_radius6.json) | other | 12464 | `e5448e62cbe385a888ec81e2006d9781c7b2fb123e4234cbb09ec087825132bd` |
| [`morphogenesis/experiments/E09_pond/l1_field_x151_radius525.json`](../morphogenesis/experiments/E09_pond/l1_field_x151_radius525.json) | other | 3626 | `c478aa0c3116bb27172f6e4b5480c5fb565f90f3e4b7e8ea9a1b57d422a0f436` |
| [`morphogenesis/experiments/E09_pond/l1_field_x153_halfcell.json`](../morphogenesis/experiments/E09_pond/l1_field_x153_halfcell.json) | other | 6180 | `09494508c7d6ade226c22678459ddfc5d911844dfea36d986c9d786df18e3792` |
| [`morphogenesis/experiments/E09_pond/l1_field_x154_mixing.json`](../morphogenesis/experiments/E09_pond/l1_field_x154_mixing.json) | other | 8206 | `1c0a59583b0833bc4b39186e046ac648b1da9e765232c558bdfcf4fecb171174` |
| [`morphogenesis/experiments/E09_pond/l1_field_x155_heredity.json`](../morphogenesis/experiments/E09_pond/l1_field_x155_heredity.json) | other | 4370 | `7eb081d6c503ebaff972da888e48f3a3f4144c957795a739cd268e55553e3e9b` |
| [`morphogenesis/experiments/E09_pond/l1_field_x156_shape_heredity.json`](../morphogenesis/experiments/E09_pond/l1_field_x156_shape_heredity.json) | other | 13075 | `6d2844c3dc0c3274f2735df932bac678f57e521b48205b76746905ce3905f6f3` |
| [`morphogenesis/experiments/E09_pond/l1_field_x157_gap_geometry.json`](../morphogenesis/experiments/E09_pond/l1_field_x157_gap_geometry.json) | other | 36967 | `08bce6becc7ef6f954f51b189e68b18ed36a78869eac055feed9a73aa19b523d` |
| [`morphogenesis/experiments/E09_pond/l1_field_x157_quantum.json`](../morphogenesis/experiments/E09_pond/l1_field_x157_quantum.json) | other | 34842 | `e2398570af874a041f67bdbd3f459f6fa19046a8d0442da4717cc41088a33626` |
| [`morphogenesis/experiments/E09_pond/l1_field_x158_crossing.json`](../morphogenesis/experiments/E09_pond/l1_field_x158_crossing.json) | other | 13433 | `09b61d2de219fa694db8d82db187b81b900302f2175b9d5a6bf87ca314f08ddd` |
| [`morphogenesis/experiments/E09_pond/l1_field_x161_discrete.json`](../morphogenesis/experiments/E09_pond/l1_field_x161_discrete.json) | other | 3189 | `305e90ca1ac0dcf63bc97f96840f11ff1a9efedd172d6bef96a3cbad77646950` |
| [`morphogenesis/experiments/E09_pond/l1_field_x162_local_scale.json`](../morphogenesis/experiments/E09_pond/l1_field_x162_local_scale.json) | other | 3000 | `faf782d5b2d4ed9b862edd16a1faadef5a401593e9eb8dfec052e6b0f4c8cee5` |
| [`morphogenesis/experiments/E09_pond/l1_field_x162b_decay.json`](../morphogenesis/experiments/E09_pond/l1_field_x162b_decay.json) | other | 1269 | `57573e4c03f14709f1a3369cfd579f62ed0c0ba6932346d868e97658010c3565` |
| [`morphogenesis/experiments/E09_pond/l1_field_x164_asymmetric.json`](../morphogenesis/experiments/E09_pond/l1_field_x164_asymmetric.json) | other | 1840 | `fb5bf0cb58c5b8a18645f2ea8f0da020d1cd94b9b4e74215d73c2bc3ff3088fd` |
| [`morphogenesis/experiments/E09_pond/l1_field_x165_three_bodies.json`](../morphogenesis/experiments/E09_pond/l1_field_x165_three_bodies.json) | other | 4652 | `7690af7df4e800773c9b43adfba60280166fe537001293afb3681c90e45efcb6` |
| [`morphogenesis/experiments/E09_pond/l1_field_x166_threshold.json`](../morphogenesis/experiments/E09_pond/l1_field_x166_threshold.json) | other | 9750 | `08b19618ead6f58ab7e22061fa39d1c9759387d91b4fd414d4b93366742c88cd` |
| [`morphogenesis/experiments/E09_pond/l1_field_x167_reversibility.json`](../morphogenesis/experiments/E09_pond/l1_field_x167_reversibility.json) | other | 8208 | `940c2db6e906db93ead3b0aa1c737ea39f1d27b001ad14bc2cd194c5a16e3e6b` |
| [`morphogenesis/experiments/E09_pond/l1_field_x167b_reversibility.json`](../morphogenesis/experiments/E09_pond/l1_field_x167b_reversibility.json) | other | 9671 | `a09b88fa70d868a2cad06da4373cc9af26b801213d4263462fd356ff0bbfbeb1` |
| [`morphogenesis/experiments/E09_pond/l1_field_x168_inflow.json`](../morphogenesis/experiments/E09_pond/l1_field_x168_inflow.json) | other | 4489 | `844b1b807208c541110e481b627a0a0832e9b34e665a5f19c78d1d227628bee9` |
| [`morphogenesis/experiments/E09_pond/l1_field_x168b_inflow_matrix.json`](../morphogenesis/experiments/E09_pond/l1_field_x168b_inflow_matrix.json) | other | 5899 | `659d5636a593d21bb58971dfcf05388896e723fa2487d0d7e37bf0dce8eb64c6` |
| [`morphogenesis/experiments/E09_pond/l1_field_x168c_inflow.json`](../morphogenesis/experiments/E09_pond/l1_field_x168c_inflow.json) | other | 9050 | `f89e0ba52475e9f142d96eae6be14a5b8a60d6ef58081c51edc788c4b25f7e31` |
| [`morphogenesis/experiments/E09_pond/l1_field_x168d_gap11.json`](../morphogenesis/experiments/E09_pond/l1_field_x168d_gap11.json) | other | 4281 | `ab4f578dc5921272def24d6b342c4456427786af1b8babd3c4f2f2f2fd3f4e56` |
| [`morphogenesis/experiments/E09_pond/l1_field_x169_seam.json`](../morphogenesis/experiments/E09_pond/l1_field_x169_seam.json) | other | 75065 | `55e9a9dbdf17abaca106cb4694d6a4a8ce2aec280c9527f784e228e930921c5b` |
| [`morphogenesis/experiments/E09_pond/l1_field_x170_corridor.json`](../morphogenesis/experiments/E09_pond/l1_field_x170_corridor.json) | other | 14729 | `fe7d2fbacdcdcac849a81e277913849df0de862956a79d9e91ec6615b05725cc` |
| [`morphogenesis/experiments/E09_pond/l1_field_x171_corridor_sizes.json`](../morphogenesis/experiments/E09_pond/l1_field_x171_corridor_sizes.json) | other | 6213 | `0108c55493c036e9950ca1cdcff0252c676335b61a694fcbf2402de1170b73a8` |
| [`morphogenesis/experiments/E09_pond/l1_field_x172_forecast.json`](../morphogenesis/experiments/E09_pond/l1_field_x172_forecast.json) | other | 4327 | `4a2d3202ae683d02cfd2e7103bdf293206f49adfd185e5a8b7dfc70d87567b95` |
| [`morphogenesis/experiments/E09_pond/l1_field_x173_bridge.json`](../morphogenesis/experiments/E09_pond/l1_field_x173_bridge.json) | other | 6458 | `4a657ea9ebf6ac3a53d19d2599075b6c7a0a6d9a8e21e6ccf6656d83bfb89984` |
| [`morphogenesis/experiments/E09_pond/l1_field_x37_eas.json`](../morphogenesis/experiments/E09_pond/l1_field_x37_eas.json) | other | 4351 | `9fddc51e4d0fe27a81da3894a0d882b62b921d0d30eba3ba2c0f6095b48bf200` |
| [`morphogenesis/experiments/E09_pond/l1_field_x56_matrix.json`](../morphogenesis/experiments/E09_pond/l1_field_x56_matrix.json) | other | 2189 | `ce629d57cf2c82b115b48ad9e6e071dcf3d7d49c180476032eeec160d15f277e` |
| [`morphogenesis/experiments/E09_pond/l1_field_x58_betti.json`](../morphogenesis/experiments/E09_pond/l1_field_x58_betti.json) | other | 24428 | `f1b4b1cde783caee0ed55d181e065e9445f8919eb678bd9a91aafacda3d08e6f` |
| [`morphogenesis/experiments/E09_pond/l1_field_x59_dose.json`](../morphogenesis/experiments/E09_pond/l1_field_x59_dose.json) | other | 1623 | `7fa68cf0edc06f88d46dacf2cc0e26f90afb84a23f93384937f0356c368ed503` |
| [`morphogenesis/experiments/E09_pond/l1_field_x61l_horizon.json`](../morphogenesis/experiments/E09_pond/l1_field_x61l_horizon.json) | other | 1684 | `726ba7b9f3b4318272bfdc3d6b6ddf36ca911812bfffa5e8affea76d9dd97539` |
| [`morphogenesis/experiments/E09_pond/l1_field_x62_scale.json`](../morphogenesis/experiments/E09_pond/l1_field_x62_scale.json) | other | 1678 | `a8df7a6cfd01cc99b3c66296e0faa5973e3eeb07fc5f065293aac32f0ae440d1` |
| [`morphogenesis/experiments/E09_pond/l1_field_x63_profile.json`](../morphogenesis/experiments/E09_pond/l1_field_x63_profile.json) | other | 1426 | `92351f7e8a6689ffef9d51b78008071caec74733e79f80227dab7dd6cb2c5101` |
| [`morphogenesis/experiments/E09_pond/l1_field_x64_refinement.json`](../morphogenesis/experiments/E09_pond/l1_field_x64_refinement.json) | other | 2114 | `006af897ad6bd8cfc306d80bc4072dbe5073d7b4d3f9236f766ed53da63bd833` |
| [`morphogenesis/experiments/E09_pond/l1_field_x65_bracket.json`](../morphogenesis/experiments/E09_pond/l1_field_x65_bracket.json) | other | 2363 | `1b28e96a3934c9b8fcf8cdba65ad6d31cc61fbf5226fc7ab8058d4232bd1ed0f` |
| [`morphogenesis/experiments/E09_pond/l1_field_x66_map.json`](../morphogenesis/experiments/E09_pond/l1_field_x66_map.json) | other | 8639 | `ae8ab91724a756e92c629a9e5c94e5be218b18292dd0c14e12ac9da3ea54b8f9` |
| [`morphogenesis/experiments/E09_pond/l1_field_x67_box.json`](../morphogenesis/experiments/E09_pond/l1_field_x67_box.json) | other | 2074 | `205de7f0e6788e68de6e164630a3a22d695e80f6846f6cfc9af0e9e231589d4b` |
| [`morphogenesis/experiments/E09_pond/l1_field_x68_identity.json`](../morphogenesis/experiments/E09_pond/l1_field_x68_identity.json) | other | 3638 | `c9a4e69b8f03b561a0cf23693427dc5d1339267c93cda25d08b4451f48c7b669` |
| [`morphogenesis/experiments/E09_pond/l1_field_x68r_identity.json`](../morphogenesis/experiments/E09_pond/l1_field_x68r_identity.json) | other | 4812 | `f85c8fb99a391ef08a9c502bddbf2afbc9f0b2cf28e299a916902965878d5172` |
| [`morphogenesis/experiments/E09_pond/l1_field_x70_size.json`](../morphogenesis/experiments/E09_pond/l1_field_x70_size.json) | other | 1358 | `8d39932ba76e8f349e96eba5b327f78db9acdc070c3195077431347932f9f906` |
| [`morphogenesis/experiments/E09_pond/l1_field_x70_spatial.json`](../morphogenesis/experiments/E09_pond/l1_field_x70_spatial.json) | other | 699 | `f141ad4a004e17fe373caade18d504560daed476993929d8607dad2aa9b14319` |
| [`morphogenesis/experiments/E09_pond/l1_field_x70_spatial_strata.json`](../morphogenesis/experiments/E09_pond/l1_field_x70_spatial_strata.json) | other | 9200 | `a14c246c344065c91f8116beba64749d1cee86ff0843e1122ed33af27bc60fb8` |
| [`morphogenesis/experiments/E09_pond/l1_field_x70r_size.json`](../morphogenesis/experiments/E09_pond/l1_field_x70r_size.json) | other | 4640 | `ce944bfa1a0d8002bdc1e213910948d3ab8f77fde3fb3a068960aa02e90bcdca` |
| [`morphogenesis/experiments/E09_pond/l1_field_x71_multistability.json`](../morphogenesis/experiments/E09_pond/l1_field_x71_multistability.json) | other | 10772 | `aeee2944e9ef1a55203ab40179520ac1044a1f4b4039381f21cc793761b12e94` |
| [`morphogenesis/experiments/E09_pond/l1_field_x71b_persistence.json`](../morphogenesis/experiments/E09_pond/l1_field_x71b_persistence.json) | other | 4055 | `f66775f4039b3a500f09d178248e8c4364119d395495ed43ded0d2f0817bf151` |
| [`morphogenesis/experiments/E09_pond/l1_field_x71c_width.json`](../morphogenesis/experiments/E09_pond/l1_field_x71c_width.json) | other | 2300 | `b4c7b6f73ebc9425b9ea06be3e282b2318de6dcc67af205866ed097ba75899a9` |
| [`morphogenesis/experiments/E09_pond/l1_field_x72_branch.json`](../morphogenesis/experiments/E09_pond/l1_field_x72_branch.json) | other | 4851 | `bdab1c4f542e7b13734ee87a2be210b8ee0cb6a1a9eed06e86224c29b0db0c32` |
| [`morphogenesis/experiments/E09_pond/l1_field_x72b_branch.json`](../morphogenesis/experiments/E09_pond/l1_field_x72b_branch.json) | other | 5969 | `b2f5f8bece2c751bbc614c87237b38fed5b84c336ccf55ac2cb74b7ac36b5fbb` |
| [`morphogenesis/experiments/E09_pond/l1_field_x72c_branch.json`](../morphogenesis/experiments/E09_pond/l1_field_x72c_branch.json) | other | 5306 | `98c0353b78eed61ff9387f11517b0b2fb3c80b7e065c9351ae0d6e83b35ae9c2` |
| [`morphogenesis/experiments/E09_pond/l1_field_x72c_regions.json`](../morphogenesis/experiments/E09_pond/l1_field_x72c_regions.json) | other | 3132 | `efc9b7b15c493440b0308f51d7ba3ef7c54161fa83041eee73843f3e8ad7e96b` |
| [`morphogenesis/experiments/E09_pond/l1_field_x72c_size_contrast.json`](../morphogenesis/experiments/E09_pond/l1_field_x72c_size_contrast.json) | other | 1654 | `2f2e547a6f6fb41f9f3479000114e7963c486bb241bfe054eaa8271f6110daad` |
| [`morphogenesis/experiments/E09_pond/l1_field_x73_depth.json`](../morphogenesis/experiments/E09_pond/l1_field_x73_depth.json) | other | 5011 | `ea66c6e1054686f39ac9496fdeae93b81439d5d5478d19db64b3dac8e02f0b1c` |
| [`morphogenesis/experiments/E09_pond/l1_field_x74_rate.json`](../morphogenesis/experiments/E09_pond/l1_field_x74_rate.json) | other | 6669 | `3fe03f151ed037080a101f0c5f6221f173df804ed830b8077486edf6123df982` |
| [`morphogenesis/experiments/E09_pond/l1_field_x75_edges.json`](../morphogenesis/experiments/E09_pond/l1_field_x75_edges.json) | other | 3752 | `6dbab031718e24d387a8f58923c83d34b91b12751f9ff5a30c2af96bb7f294f9` |
| [`morphogenesis/experiments/E09_pond/l1_field_x76_033.json`](../morphogenesis/experiments/E09_pond/l1_field_x76_033.json) | other | 3123 | `67fbb93650cf98c3a8b823b42ce50acacdf0d39d4f1bc6eea471e60a1e2e62f3` |
| [`morphogenesis/experiments/E09_pond/l1_field_x77_patch.json`](../morphogenesis/experiments/E09_pond/l1_field_x77_patch.json) | other | 1238 | `f940884fb04dc551020ff0645d92c249fae73219307e373bd1d548b631c2b3b6` |
| [`morphogenesis/experiments/E09_pond/l1_field_x78_causal.json`](../morphogenesis/experiments/E09_pond/l1_field_x78_causal.json) | other | 7257 | `5c88d8b9d895515d78714a2f0b4820c74bfe8c0423d6f02a46698f468d82a1db` |
| [`morphogenesis/experiments/E09_pond/l1_field_x78b_causal.json`](../morphogenesis/experiments/E09_pond/l1_field_x78b_causal.json) | other | 5496 | `0f6fb2a00c7b400c7ea9f5dccf248c23241d50d051b61798ae6f4e587577c6aa` |
| [`morphogenesis/experiments/E09_pond/l1_field_x79_mix.json`](../morphogenesis/experiments/E09_pond/l1_field_x79_mix.json) | other | 6369 | `dc86079345d14da59f3b70b88acbb3467a3ed2fc4efccabb8a8acec2e7738314` |
| [`morphogenesis/experiments/E09_pond/l1_field_x80_dip.json`](../morphogenesis/experiments/E09_pond/l1_field_x80_dip.json) | other | 6142 | `f45a69ffaa1c019bcb065ff66bf3fac3d6ba587bfbda05598363a90bbcddeaa0` |
| [`morphogenesis/experiments/E09_pond/l1_field_x82_reach.json`](../morphogenesis/experiments/E09_pond/l1_field_x82_reach.json) | other | 16068 | `b5905d84b387728a76fb0199281ff9e5cd0bbda6137097277a915b12d6257417` |
| [`morphogenesis/experiments/E09_pond/l1_field_x84_angular.json`](../morphogenesis/experiments/E09_pond/l1_field_x84_angular.json) | other | 6236 | `a3c52e023bfc2dac1257e3c9e5609a518d2edae54e47d453af2fedc2ec9078e3` |
| [`morphogenesis/experiments/E09_pond/l1_field_x85_symmetry_memory.json`](../morphogenesis/experiments/E09_pond/l1_field_x85_symmetry_memory.json) | other | 12284 | `e54a5737ee3d6ff2d6cb9458f2fbe1f75ba3af3055ca2bf16978dd5166d45123` |
| [`morphogenesis/experiments/E09_pond/l1_field_x86_symmetry_curve.json`](../morphogenesis/experiments/E09_pond/l1_field_x86_symmetry_curve.json) | other | 25954 | `16956545f72d89c499c0e74c3843d3ddf244056f58220eeae9a3f62dd4853337` |
| [`morphogenesis/experiments/E09_pond/l1_field_x87_memory_vs_symmetry.json`](../morphogenesis/experiments/E09_pond/l1_field_x87_memory_vs_symmetry.json) | other | 27551 | `7327bf66ca914e0ba640c54b0386b5cc6ac53290d95168e2b0d099fba6d79e2c` |
| [`morphogenesis/experiments/E09_pond/l1_field_x88_percolating_arm.json`](../morphogenesis/experiments/E09_pond/l1_field_x88_percolating_arm.json) | other | 25413 | `35f5da486e531448a0a9366783c4356117e792155fc28ae4d22789b1d99c173e` |
| [`morphogenesis/experiments/E09_pond/l1_field_x89_lineage_edge.json`](../morphogenesis/experiments/E09_pond/l1_field_x89_lineage_edge.json) | other | 2357 | `2798678dc68c3ed5483e0ae9403d4afe9a0741fc3673680a8ca351f5becdad8f` |
| [`morphogenesis/experiments/E09_pond/l1_field_x90_trickle.json`](../morphogenesis/experiments/E09_pond/l1_field_x90_trickle.json) | other | 1807 | `7a08008a328eb5aaaefe954f1db2c7251582ded4c95ae33c9190648e98496ce5` |
| [`morphogenesis/experiments/E09_pond/l1_field_x91_lineage_specificity.json`](../morphogenesis/experiments/E09_pond/l1_field_x91_lineage_specificity.json) | other | 2253 | `5ee60d1ada87afd516046a985bee52e3a3e486a1a8214497b93181b9784b3701` |
| [`morphogenesis/experiments/E09_pond/l1_field_x92_pay.json`](../morphogenesis/experiments/E09_pond/l1_field_x92_pay.json) | other | 2075 | `8f5169c00567503bbcf00af8c3244515de071bfc54f1affd4587c0a43a27fb62` |
| [`morphogenesis/experiments/E09_pond/l1_field_x93_sibling_contrast.json`](../morphogenesis/experiments/E09_pond/l1_field_x93_sibling_contrast.json) | other | 1734 | `30b2bd0bc0134a2b051175f57a4bd03d470b65a48f1faf0a719542fd39ac2a19` |
| [`morphogenesis/experiments/E09_pond/l1_field_x96_pilot.json`](../morphogenesis/experiments/E09_pond/l1_field_x96_pilot.json) | other | 2611 | `5c8966d76405b9cef9617a8102d3f09c1718db384d6cd8ecc8336ae67eb4da9c` |
| [`morphogenesis/experiments/E09_pond/l1_field_x96b_pilot.json`](../morphogenesis/experiments/E09_pond/l1_field_x96b_pilot.json) | other | 3306 | `46f9bb4a74c067dc1e8834319da5e4aec82d6a9ea0a5ac96415fc843987d7d0e` |
| [`morphogenesis/experiments/E09_pond/l1_field_x96c_pilot.json`](../morphogenesis/experiments/E09_pond/l1_field_x96c_pilot.json) | other | 3306 | `46f9bb4a74c067dc1e8834319da5e4aec82d6a9ea0a5ac96415fc843987d7d0e` |
| [`morphogenesis/experiments/E09_pond/l1_field_x96d_orientation.json`](../morphogenesis/experiments/E09_pond/l1_field_x96d_orientation.json) | other | 7354 | `331ee438f36129aad5b1bef2f852f9e6e0cb8aae9cb95efe5996919cbb19ae7b` |
| [`morphogenesis/experiments/E09_pond/l1_field_x97_sisters_second_generation.json`](../morphogenesis/experiments/E09_pond/l1_field_x97_sisters_second_generation.json) | other | 1459 | `4a70c3acfb3a469ce9bc047b34d196d59256d7eb26d1214902c67b66021c11ff` |
| [`morphogenesis/experiments/E09_pond/l1_field_x97b_sisters_median.json`](../morphogenesis/experiments/E09_pond/l1_field_x97b_sisters_median.json) | other | 1084 | `03ddf4a44ef10b0f5ffd45e3020672294542400efcc97b906aeb71810d610dab` |
| [`morphogenesis/experiments/E09_pond/l1_field_x98_threshold.json`](../morphogenesis/experiments/E09_pond/l1_field_x98_threshold.json) | other | 6903 | `d66445f799ff5d6e40983c70edae6bd7a31fa8bc3ab42f81b996d70307396eb1` |
| [`morphogenesis/experiments/E09_pond/l1_field_x99_threshold_memory.json`](../morphogenesis/experiments/E09_pond/l1_field_x99_threshold_memory.json) | other | 2888 | `735c71d8d6399ed99bf42b238e0053d0f0d2160f755f72fa133a68e508d907f2` |
| [`morphogenesis/experiments/E09_pond/l2_matrix.json`](../morphogenesis/experiments/E09_pond/l2_matrix.json) | other | 9877 | `066d9b748d3be92f8122002dc6c28aaa5297eff8055b06580d5a4c23f1ad0e9b` |
| [`morphogenesis/experiments/E09_pond/merge_keep_matrix.json`](../morphogenesis/experiments/E09_pond/merge_keep_matrix.json) | other | 17866 | `41f5ff962f61e6b2d34b432149dbb1b063bb4e9f451271d3f65ad9e0192c8804` |
| [`morphogenesis/experiments/E09_pond/mergekeep_keep_seed1.json`](../morphogenesis/experiments/E09_pond/mergekeep_keep_seed1.json) | other | 169196 | `bc661f89a6290dd63693c1647f7e14abc1481b432dffae0b711fb15d39b6a47e` |
| [`morphogenesis/experiments/E09_pond/mergekeep_keep_seed10.json`](../morphogenesis/experiments/E09_pond/mergekeep_keep_seed10.json) | other | 168707 | `cfa02af37184195baa2aaf7bc9983707567ae31156a5adb55a22c3feb8891acc` |
| [`morphogenesis/experiments/E09_pond/mergekeep_keep_seed2.json`](../morphogenesis/experiments/E09_pond/mergekeep_keep_seed2.json) | other | 168070 | `127101f26a8f812091fb23612a7f03230c780129a740c4483178f49b9845c15b` |
| [`morphogenesis/experiments/E09_pond/mergekeep_keep_seed3.json`](../morphogenesis/experiments/E09_pond/mergekeep_keep_seed3.json) | other | 168538 | `4ef884384ccac54445f328ebb8f53a24b673c2a62a7799a1b67b86d4afbd1548` |
| [`morphogenesis/experiments/E09_pond/mergekeep_keep_seed4.json`](../morphogenesis/experiments/E09_pond/mergekeep_keep_seed4.json) | other | 168888 | `702c2ad42d1bc3a2d4604bd876d5d0a8923d7ab88b98ef6244d831f3c51230ec` |
| [`morphogenesis/experiments/E09_pond/mergekeep_keep_seed5.json`](../morphogenesis/experiments/E09_pond/mergekeep_keep_seed5.json) | other | 168585 | `482f291b248218923d979dcbffae5227c042f5f191e28b2b922939526a87cea5` |
| [`morphogenesis/experiments/E09_pond/mergekeep_keep_seed6.json`](../morphogenesis/experiments/E09_pond/mergekeep_keep_seed6.json) | other | 168718 | `2eac672f07d9c21bcb84bb2973039018e3f7296144033032a393668a416a8885` |
| [`morphogenesis/experiments/E09_pond/mergekeep_keep_seed7.json`](../morphogenesis/experiments/E09_pond/mergekeep_keep_seed7.json) | other | 168922 | `691c7a2cea159859c6bd031c28d2f5bffd274264f91b3e1ba73b072ce2da05d3` |
| [`morphogenesis/experiments/E09_pond/mergekeep_keep_seed8.json`](../morphogenesis/experiments/E09_pond/mergekeep_keep_seed8.json) | other | 168505 | `9b5df4aec9930ca726e10c036c15c775420621b7a096b6c670426dbc8be44194` |
| [`morphogenesis/experiments/E09_pond/mergekeep_keep_seed9.json`](../morphogenesis/experiments/E09_pond/mergekeep_keep_seed9.json) | other | 168279 | `50654c3f516d7b854f025dd4e3979dd8508c858b9354d303fcba774ec3c31c52` |
| [`morphogenesis/experiments/E09_pond/mergekeep_majority_seed1.json`](../morphogenesis/experiments/E09_pond/mergekeep_majority_seed1.json) | other | 168777 | `fb8ed54ad0d946c64b3fa4c128d57f251ea83d085f0c679be8d2d1fa529621c8` |
| [`morphogenesis/experiments/E09_pond/mergekeep_majority_seed10.json`](../morphogenesis/experiments/E09_pond/mergekeep_majority_seed10.json) | other | 168473 | `539d1aab7de43b08cb8b1678a6280ccff0e39a8f5d3d513a7c29ee598ea7d72b` |
| [`morphogenesis/experiments/E09_pond/mergekeep_majority_seed2.json`](../morphogenesis/experiments/E09_pond/mergekeep_majority_seed2.json) | other | 168072 | `71f3538b38f31ffe93db105aa1c12df278b41ca4703ae094eb7ec176caba8a4a` |
| [`morphogenesis/experiments/E09_pond/mergekeep_majority_seed3.json`](../morphogenesis/experiments/E09_pond/mergekeep_majority_seed3.json) | other | 168235 | `69846da25733284ee67cff461caf4cd3bd073c3368f9e2a2a2a7fa6fb0a7e44c` |
| [`morphogenesis/experiments/E09_pond/mergekeep_majority_seed4.json`](../morphogenesis/experiments/E09_pond/mergekeep_majority_seed4.json) | other | 168876 | `0a11b77da0404547b16c0661684948b56af15da5f561f9d3c6e88be87be8badb` |
| [`morphogenesis/experiments/E09_pond/mergekeep_majority_seed5.json`](../morphogenesis/experiments/E09_pond/mergekeep_majority_seed5.json) | other | 168479 | `e74842cfa287b2c3e99fe7cf7210f1802bb3341317d08484bd285985d4f30f9a` |
| [`morphogenesis/experiments/E09_pond/mergekeep_majority_seed6.json`](../morphogenesis/experiments/E09_pond/mergekeep_majority_seed6.json) | other | 168719 | `f20af8fc1c5a6af0a558b7937c2b4982dac9a61dbb3be8ce4d602b33b20e9caf` |
| [`morphogenesis/experiments/E09_pond/mergekeep_majority_seed7.json`](../morphogenesis/experiments/E09_pond/mergekeep_majority_seed7.json) | other | 168733 | `69b601cfcf096393be4b6f76e40261fd20b50c7381d2b458971b76276d332230` |
| [`morphogenesis/experiments/E09_pond/mergekeep_majority_seed8.json`](../morphogenesis/experiments/E09_pond/mergekeep_majority_seed8.json) | other | 168338 | `e029d4957f0140d7f248608df7dbabd83dfe77ad1093a65cdc81612a28ef02f9` |
| [`morphogenesis/experiments/E09_pond/mergekeep_majority_seed9.json`](../morphogenesis/experiments/E09_pond/mergekeep_majority_seed9.json) | other | 168280 | `738131e618934cff0c63e00eb1dfa7767f8983692855f503413db69ddd584ada` |
| [`morphogenesis/experiments/E09_pond/metric_variants.json`](../morphogenesis/experiments/E09_pond/metric_variants.json) | other | 114678 | `dd6bcbdae55eb0b172b6df7b885b9a24d19ee4cd8e3116f6b22f6f5a94b45ff4` |
| [`morphogenesis/experiments/E09_pond/metric_variants_d2.json`](../morphogenesis/experiments/E09_pond/metric_variants_d2.json) | other | 115074 | `18d58a3bc913a77ee63b7b9a2794ade2211273d608e2112ca9ce69caeab04cac` |
| [`morphogenesis/experiments/E09_pond/metric_variants_d2rep.json`](../morphogenesis/experiments/E09_pond/metric_variants_d2rep.json) | other | 118386 | `7aa6f17003a3607bcc176050ca3f2be6bd366bc96c98383a465c22959722ae05` |
| [`morphogenesis/experiments/E09_pond/metric_variants_d2rep_n1.json`](../morphogenesis/experiments/E09_pond/metric_variants_d2rep_n1.json) | other | 115157 | `bb384481cc395abd179e839ef86eef17241cf29d1126c24ea64f37dcdea661f5` |
| [`morphogenesis/experiments/E09_pond/metric_variants_onebud.json`](../morphogenesis/experiments/E09_pond/metric_variants_onebud.json) | other | 118348 | `6c6e45738e111cbf01733ab13527204972867cd7c4712415eeb1d02b90584ef0` |
| [`morphogenesis/experiments/E09_pond/mobility_matrix.json`](../morphogenesis/experiments/E09_pond/mobility_matrix.json) | other | 13597 | `b90f56fd22fb5d3de9d78cbd5aa573b42a86fcd3b4eae60e4b4f1ce69ef68c37` |
| [`morphogenesis/experiments/E09_pond/mut_m0001_seed1.json`](../morphogenesis/experiments/E09_pond/mut_m0001_seed1.json) | other | 167982 | `e5ce0066748446e68682a046be58671da8e1cad4daf24bc29a43488360b9795d` |
| [`morphogenesis/experiments/E09_pond/mut_m0001_seed2.json`](../morphogenesis/experiments/E09_pond/mut_m0001_seed2.json) | other | 167387 | `85aeda83beed2dda5e20e507a972375c109b779214cfa3f96304971b4d926113` |
| [`morphogenesis/experiments/E09_pond/mut_m0001_seed3.json`](../morphogenesis/experiments/E09_pond/mut_m0001_seed3.json) | other | 166976 | `e491da164e8904420e7853c808582935e5a76c85f17499e27e0e2353f46a8ff2` |
| [`morphogenesis/experiments/E09_pond/mut_m001_seed1.json`](../morphogenesis/experiments/E09_pond/mut_m001_seed1.json) | other | 174778 | `6fb6d000fa0f506d85a35672eb20347e639d4591d0cd08ee7a4e166a45859880` |
| [`morphogenesis/experiments/E09_pond/mut_m001_seed2.json`](../morphogenesis/experiments/E09_pond/mut_m001_seed2.json) | other | 176477 | `c3ab9c1a1874ea62fb0ff32b1387c88ece7b90c5238bf432e10fd06ed25437e1` |
| [`morphogenesis/experiments/E09_pond/mut_m001_seed3.json`](../morphogenesis/experiments/E09_pond/mut_m001_seed3.json) | other | 172641 | `c386cd10141ab10e6c7c4e61d7f100b38d8288c0e4b0eb365dc6418ad821d6e9` |
| [`morphogenesis/experiments/E09_pond/mut_m005_seed1.json`](../morphogenesis/experiments/E09_pond/mut_m005_seed1.json) | other | 206288 | `5d903ab39c91c4c6510896b49b4f7e46c3f4b46484dfef08654d8af03c532de8` |
| [`morphogenesis/experiments/E09_pond/mut_m005_seed2.json`](../morphogenesis/experiments/E09_pond/mut_m005_seed2.json) | other | 216563 | `79af2387a022974e2edfb98a4c762c8322150c8db5d0b902f0b102497c035dde` |
| [`morphogenesis/experiments/E09_pond/mut_m005_seed3.json`](../morphogenesis/experiments/E09_pond/mut_m005_seed3.json) | other | 199487 | `37536d11fe2c6505c89e54c2a0723d65abf6fe5aaaa23135b3791a31918e390f` |
| [`morphogenesis/experiments/E09_pond/mut_m02_seed1.json`](../morphogenesis/experiments/E09_pond/mut_m02_seed1.json) | other | 336020 | `1a482ba860954aca39acfe81f57227f0ff7c62d0066385ffe9d44df9cd48bcf2` |
| [`morphogenesis/experiments/E09_pond/mut_m02_seed2.json`](../morphogenesis/experiments/E09_pond/mut_m02_seed2.json) | other | 354237 | `4e40d808e43def1c81f865a9c11a192c94c74c5699a9977fb782a53746e7fb9d` |
| [`morphogenesis/experiments/E09_pond/mut_m02_seed3.json`](../morphogenesis/experiments/E09_pond/mut_m02_seed3.json) | other | 300815 | `848c21d05adfaa7ace28d296521133e19509aec5826136ff647d0e86e7b0d695` |
| [`morphogenesis/experiments/E09_pond/mut_m0_seed1.json`](../morphogenesis/experiments/E09_pond/mut_m0_seed1.json) | other | 167026 | `2fc3d6d7855b8c4b27c34c4530ff76d3ff47d42539c6238b75baaa262c096154` |
| [`morphogenesis/experiments/E09_pond/mut_m0_seed2.json`](../morphogenesis/experiments/E09_pond/mut_m0_seed2.json) | other | 167114 | `b7f3b9c8b3dd9096930504cf5a6c6967eb2c807a3ed5c040905fe94f7d3fde9c` |
| [`morphogenesis/experiments/E09_pond/mut_m0_seed3.json`](../morphogenesis/experiments/E09_pond/mut_m0_seed3.json) | other | 166748 | `fda20b0986a4d05033c90323ca8ea67a074dc25cb314627e9139d34204a5f380` |
| [`morphogenesis/experiments/E09_pond/mutation_matrix.json`](../morphogenesis/experiments/E09_pond/mutation_matrix.json) | other | 15733 | `5b9ed3ea6d3f58b0f6290f3e448487ed28d1430bb3489b43010332639b81a69e` |
| [`morphogenesis/experiments/E09_pond/organism_mobility_matrix.json`](../morphogenesis/experiments/E09_pond/organism_mobility_matrix.json) | other | 10829 | `88b7d55945e85d1b02c6cc97ae13b70f853ea4269ff9a7f25086ef949e2f51a3` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at201_seed1.json`](../morphogenesis/experiments/E09_pond/phase/phase_at201_seed1.json) | other | 169870 | `ee9a29a7d29c10ab977bc233a3584305c55c7d649be2d83f9ef64979d7e3bb99` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at201_seed10.json`](../morphogenesis/experiments/E09_pond/phase/phase_at201_seed10.json) | other | 169446 | `5ef52e44c6ca9cc700b689d107e1edec73e34def46b7e5084c275f4ef5c0c7bc` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at201_seed2.json`](../morphogenesis/experiments/E09_pond/phase/phase_at201_seed2.json) | other | 169506 | `a9ddab531fc309cf554ff65a3e4076ba8dfac26dc37db08c96eb2cd440d5ef8a` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at201_seed3.json`](../morphogenesis/experiments/E09_pond/phase/phase_at201_seed3.json) | other | 169229 | `d85a9665ff801e0d562117d340dcf0c8e268b91fb88d2e44b54c0e6b3139ef18` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at201_seed4.json`](../morphogenesis/experiments/E09_pond/phase/phase_at201_seed4.json) | other | 169755 | `ae99b7710be8401ae64e3232969550c682f0778b857e6674303dd6aef2b7bfb5` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at201_seed5.json`](../morphogenesis/experiments/E09_pond/phase/phase_at201_seed5.json) | other | 169485 | `2d52c004d9499b2a99c1e4fc38ba80b0684360748798552fc988d8da5e7f35af` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at201_seed6.json`](../morphogenesis/experiments/E09_pond/phase/phase_at201_seed6.json) | other | 169616 | `bfb2b354efac94e867b2e88ca0c64c4f5815530d4bf4c6afe5c6c41cb5bf4cfe` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at201_seed7.json`](../morphogenesis/experiments/E09_pond/phase/phase_at201_seed7.json) | other | 169781 | `fb9ae7bc3e87b9ee9a185f3e4c74b9631d404a58ebbd52be13e290f7e8530185` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at201_seed8.json`](../morphogenesis/experiments/E09_pond/phase/phase_at201_seed8.json) | other | 169092 | `cb4b3eb64f9b2fb0b4e46a94922a2f074589a983905be3592c819353c49fa61e` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at201_seed9.json`](../morphogenesis/experiments/E09_pond/phase/phase_at201_seed9.json) | other | 169086 | `dfa5692b08186f07036361c53c36ff602afdb7ce1069a6f071d9cda8e65ddb0d` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at202_seed1.json`](../morphogenesis/experiments/E09_pond/phase/phase_at202_seed1.json) | other | 169788 | `91447393f9bd7913b3b6da612d56aeeb088574323da25993e278a1c8f730d3e4` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at202_seed10.json`](../morphogenesis/experiments/E09_pond/phase/phase_at202_seed10.json) | other | 169376 | `02d82b823a84f9c096d508a7c505e70d0df00a83c739f5d14b0bae11f30b28ad` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at202_seed2.json`](../morphogenesis/experiments/E09_pond/phase/phase_at202_seed2.json) | other | 169603 | `be4f0fc8f2ae4ba147526a388424116c08723c87da2e30e31f1f8b3f79d141ba` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at202_seed3.json`](../morphogenesis/experiments/E09_pond/phase/phase_at202_seed3.json) | other | 169252 | `d008fbae02ccc0283b66b596772fc574b7e02e8c9dba8471da5d8b66061f0710` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at202_seed4.json`](../morphogenesis/experiments/E09_pond/phase/phase_at202_seed4.json) | other | 169637 | `c4b93f3347fd28cd05dbc38aaa64e402af494b59a7b30b7495af43a079cc74a3` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at202_seed5.json`](../morphogenesis/experiments/E09_pond/phase/phase_at202_seed5.json) | other | 169337 | `90255b6c7d10e9ad3c585793d5110484f091ccc6cc5f773221093278a1c65f64` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at202_seed6.json`](../morphogenesis/experiments/E09_pond/phase/phase_at202_seed6.json) | other | 169646 | `f769e98ac39a9ce678006b05d47b8b4af3841624a61a11eaa12031691febf1d5` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at202_seed7.json`](../morphogenesis/experiments/E09_pond/phase/phase_at202_seed7.json) | other | 169739 | `b3e5dd0a77355172c0f94eadcad65f956ad2bc821406415f983005947cd58204` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at202_seed8.json`](../morphogenesis/experiments/E09_pond/phase/phase_at202_seed8.json) | other | 169240 | `25133204acc53c715317dad428e96fc448cd913509c57e97e252d655075956f8` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at202_seed9.json`](../morphogenesis/experiments/E09_pond/phase/phase_at202_seed9.json) | other | 169083 | `c9fa90789caeee91ae835f7694c291ffd5c3fc614791ef34fcf6257633dbea6c` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at203_seed1.json`](../morphogenesis/experiments/E09_pond/phase/phase_at203_seed1.json) | other | 169830 | `853abb95daa6bc62a8f12d322a8b8d4b977207d3e4b501d401f368df554da11b` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at203_seed10.json`](../morphogenesis/experiments/E09_pond/phase/phase_at203_seed10.json) | other | 169439 | `26d3fd42723c1b56a2180b0d01f497040cb6956814657a3423d929e9e754b427` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at203_seed2.json`](../morphogenesis/experiments/E09_pond/phase/phase_at203_seed2.json) | other | 169469 | `72b3dfbda5c891577d40cfae2910615af4eb17fe43c9b097dcdd4fa25d1e1782` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at203_seed3.json`](../morphogenesis/experiments/E09_pond/phase/phase_at203_seed3.json) | other | 169129 | `0ba69ec07d09ac9e0391e29b60639cfbb266e59f9f7b97bc7874a4bbc2d23f87` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at203_seed4.json`](../morphogenesis/experiments/E09_pond/phase/phase_at203_seed4.json) | other | 169630 | `c32a776b50befb9924b2c66a448fa7087c20f90338891c12b713df35aee4c48e` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at203_seed5.json`](../morphogenesis/experiments/E09_pond/phase/phase_at203_seed5.json) | other | 169425 | `3f1369fe60f11b14909c269be96f3f416bdce73343ee1cfc2e3d64aaa1ac2430` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at203_seed6.json`](../morphogenesis/experiments/E09_pond/phase/phase_at203_seed6.json) | other | 169506 | `13569cbcd455d03b2ba62ef7fd5bb72f81f0ab28ace29060297b64a24175f5fe` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at203_seed7.json`](../morphogenesis/experiments/E09_pond/phase/phase_at203_seed7.json) | other | 169689 | `777eb4a0686fde7d2dfaf9efeb9f9bd784f6fdd1e7e01378887fad203584faee` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at203_seed8.json`](../morphogenesis/experiments/E09_pond/phase/phase_at203_seed8.json) | other | 169395 | `848be1c4160737ea6a27541ee041379ccbf391e4e3e1dcd7a2b3a7aeb1fcb0ec` |
| [`morphogenesis/experiments/E09_pond/phase/phase_at203_seed9.json`](../morphogenesis/experiments/E09_pond/phase/phase_at203_seed9.json) | other | 168962 | `856e3c3c3dcfd36e9e0dc8440db6d5a091fd92e9faaec96f5db57317f5ebf146` |
| [`morphogenesis/experiments/E09_pond/phase_matrix.json`](../morphogenesis/experiments/E09_pond/phase_matrix.json) | other | 17508 | `eb87e900271f59522fd1fa20ca5b70b1e66e718302210444a8db5708af2db4f6` |
| [`morphogenesis/experiments/E09_pond/pilot_lineage_seed1.json`](../morphogenesis/experiments/E09_pond/pilot_lineage_seed1.json) | other | 482549 | `5e2171382b5fe72cb38299a914b9b64266d9372ddc0593fe3968b84b38ef36fa` |
| [`morphogenesis/experiments/E09_pond/placement/placement_diag_keep_seed2.json`](../morphogenesis/experiments/E09_pond/placement/placement_diag_keep_seed2.json) | other | 170255 | `a80b5a24a2beae871a98e25e6b09926014754f959f7497b60da3af8a65b1cc7e` |
| [`morphogenesis/experiments/E09_pond/placement/placement_diag_majority_seed2.json`](../morphogenesis/experiments/E09_pond/placement/placement_diag_majority_seed2.json) | other | 169875 | `a022fa3417b444eb9fc6d9fc1388b2fd1a7d588307a916bd885e87884d947766` |
| [`morphogenesis/experiments/E09_pond/placement/placement_keep_seed1.json`](../morphogenesis/experiments/E09_pond/placement/placement_keep_seed1.json) | other | 170298 | `2d6504f21d45fe03bc9e75b4848945b7d155fe3e059635ad12a7eb977579e0e7` |
| [`morphogenesis/experiments/E09_pond/placement/placement_keep_seed10.json`](../morphogenesis/experiments/E09_pond/placement/placement_keep_seed10.json) | other | 170128 | `b12a3aa12db506d49a0ed1d75a0bf5ab047730d7ad6e20d9053a77dbc6f7c141` |
| [`morphogenesis/experiments/E09_pond/placement/placement_keep_seed2.json`](../morphogenesis/experiments/E09_pond/placement/placement_keep_seed2.json) | other | 170257 | `9a48c1c5075b623f0414bcbc89088ad56a05fa9bac67aa898078dcfd831538eb` |
| [`morphogenesis/experiments/E09_pond/placement/placement_keep_seed3.json`](../morphogenesis/experiments/E09_pond/placement/placement_keep_seed3.json) | other | 169738 | `376a8f0d87bd2cd7a8e49b7144420c8780bf043c658a653553ebe34eac23fd97` |
| [`morphogenesis/experiments/E09_pond/placement/placement_keep_seed4.json`](../morphogenesis/experiments/E09_pond/placement/placement_keep_seed4.json) | other | 170467 | `a2d2c5c4f210e67b487ce6d8572f073cf459d8712c4b08cee8cb21a295dab5c0` |
| [`morphogenesis/experiments/E09_pond/placement/placement_keep_seed5.json`](../morphogenesis/experiments/E09_pond/placement/placement_keep_seed5.json) | other | 170060 | `9c7d1fe8b075b8cb085803568600978b3920e8f91d06bc915d16548450e3c47d` |
| [`morphogenesis/experiments/E09_pond/placement/placement_keep_seed6.json`](../morphogenesis/experiments/E09_pond/placement/placement_keep_seed6.json) | other | 170356 | `adf2dfe72c720a2b74da16ae6dcec8e93be733ed8553361c5ddb2e077498af48` |
| [`morphogenesis/experiments/E09_pond/placement/placement_keep_seed7.json`](../morphogenesis/experiments/E09_pond/placement/placement_keep_seed7.json) | other | 170091 | `637655bb71910beb1bd6e3816e530159226fd86b284caa062bf70928896c1489` |
| [`morphogenesis/experiments/E09_pond/placement/placement_keep_seed8.json`](../morphogenesis/experiments/E09_pond/placement/placement_keep_seed8.json) | other | 170088 | `cd35adb885b6300eee42b26c6d1e6e6cd0a5732469297072ffe3686089af25ac` |
| [`morphogenesis/experiments/E09_pond/placement/placement_keep_seed9.json`](../morphogenesis/experiments/E09_pond/placement/placement_keep_seed9.json) | other | 169656 | `668a3024ea3722820b14481a02097ff4b0477079777bb1345e97f367e9603fc9` |
| [`morphogenesis/experiments/E09_pond/placement/placement_majority_seed1.json`](../morphogenesis/experiments/E09_pond/placement/placement_majority_seed1.json) | other | 170032 | `4e587acf73a97c36502ad7c57aa4e9c7062b653d6322162e920572893795df8d` |
| [`morphogenesis/experiments/E09_pond/placement/placement_majority_seed10.json`](../morphogenesis/experiments/E09_pond/placement/placement_majority_seed10.json) | other | 169652 | `dca7c1036f851bbe096352f43b56d1585bc5a7d9ba6dc76df7e79490164edb52` |
| [`morphogenesis/experiments/E09_pond/placement/placement_majority_seed2.json`](../morphogenesis/experiments/E09_pond/placement/placement_majority_seed2.json) | other | 169874 | `712ab9672ca8f8bc975fe5f818872df0ef275560b240e7cc6afff001d2cc1773` |
| [`morphogenesis/experiments/E09_pond/placement/placement_majority_seed3.json`](../morphogenesis/experiments/E09_pond/placement/placement_majority_seed3.json) | other | 169262 | `7eab323e2fdbbcdd8514be2010b3f0d2c99d778e272df383a4fc3beddc43fa4e` |
| [`morphogenesis/experiments/E09_pond/placement/placement_majority_seed4.json`](../morphogenesis/experiments/E09_pond/placement/placement_majority_seed4.json) | other | 170096 | `2087d4b18fd384db3d372674d6ea0a917576a05b22e834396aa0de574e11ff51` |
| [`morphogenesis/experiments/E09_pond/placement/placement_majority_seed5.json`](../morphogenesis/experiments/E09_pond/placement/placement_majority_seed5.json) | other | 169708 | `bab56b55d65509f0ed7c2634cf5ae376862d16b0e50e4ac0985a5058036b9130` |
| [`morphogenesis/experiments/E09_pond/placement/placement_majority_seed6.json`](../morphogenesis/experiments/E09_pond/placement/placement_majority_seed6.json) | other | 169920 | `d99702789cbd1284c1ffaba1f68937221df4a4e2179697544f95c8557d2c06d9` |
| [`morphogenesis/experiments/E09_pond/placement/placement_majority_seed7.json`](../morphogenesis/experiments/E09_pond/placement/placement_majority_seed7.json) | other | 169974 | `8c7b300ef785020466725ab7f1a3fafdcdf919432a2b41ce97590ab1014d8393` |
| [`morphogenesis/experiments/E09_pond/placement/placement_majority_seed8.json`](../morphogenesis/experiments/E09_pond/placement/placement_majority_seed8.json) | other | 169636 | `e6df9990490877ca004b5e969adb8662db71ea70e584af7b6e3537b99beef303` |
| [`morphogenesis/experiments/E09_pond/placement/placement_majority_seed9.json`](../morphogenesis/experiments/E09_pond/placement/placement_majority_seed9.json) | other | 169321 | `49d829c6f1499593b1acc7ef7ec0d8fdbd6de6aaed853aff1e27177e577a6f3d` |
| [`morphogenesis/experiments/E09_pond/placement_matrix.json`](../morphogenesis/experiments/E09_pond/placement_matrix.json) | other | 12684 | `8e5a2a20b994c5d1138ab636a3a374bcb4385dbd729264dba2b321c29efe296a` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed1.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed1.json) | other | 170387 | `2d11aa80e0716c90659aaf5800af7767913de0bf31837c7293e343e0a1f00592` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed10.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed10.json) | other | 170321 | `e4cb0d09c89d36d83719936550b98858542db0b4f0613fb749bc450ef52ea5c4` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed2.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed2.json) | other | 170660 | `ebb87838eeacc123c224012cba6270e12901837bec248ed8af4ed31fb73d2252` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed3.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed3.json) | other | 170017 | `3f27de6169d3bc32924593b48023500e229060a33b640cdce820a63bc183d752` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed4.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed4.json) | other | 170159 | `07eba44dda17eac2b5ed6d8038c953b0f30696f0ad00cee757bc7f5c7c4f312e` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed5.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed5.json) | other | 170556 | `4c2bb4d0269d612b690c966464f1ed0fbd2bf1bd94e2e2bfa4236cb766fed484` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed6.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed6.json) | other | 170255 | `2b123737fac664fc316adcbe34f32c75eccb3a1fdeec4648b25df6e1887431aa` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed7.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed7.json) | other | 170401 | `59d561451916146a4fbee7098f3ac3bad777a0058ad1694105d65cbb7c74e50d` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed8.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed8.json) | other | 170206 | `b12252ef77a42d5ae9161c8c25444d322afe4f2afeb974bb641a4c0237c42946` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed9.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_keep_seed9.json) | other | 170069 | `b24ae25f027ab447590676d3e6edcab28806d5330383260d07da4792ad344d3c` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed1.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed1.json) | other | 170015 | `9cb3183cbc6b8aba8339c7d3b1991cb9f59051c8471cb450b5de0fbdebcb3835` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed10.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed10.json) | other | 169896 | `b135679deb3c1d828adcb644e1082e1d6886c3892cfe21a1787d12d89020eac5` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed2.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed2.json) | other | 170101 | `a8d6aaa784e221fcd0a4a3570a9a5bc53a430e7baafaf5a511347176930db1e4` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed3.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed3.json) | other | 169544 | `c508d280e079b0f71ae00b119bc35d3f1a32a8d073adc64cafa8abfa22e8c3b3` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed4.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed4.json) | other | 169585 | `0eaf830ffed24a227eb2af34b8b7288b4289619ef268a1076c87c01b5cef1c66` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed5.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed5.json) | other | 170082 | `563b19f176b222531169b9fab92d8f02f3b8e4241a7a8a0e64d6c2705697b66f` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed6.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed6.json) | other | 169731 | `6c71dfcadda156afcd3fcedc5746304f596e407401abb00e3a36c091948a2ca3` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed7.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed7.json) | other | 170016 | `b06954c96c97979946a534f6bbfebeecd7bc89f994da4a31acd38aecf641eab4` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed8.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed8.json) | other | 169928 | `874ab39ca92b3dd62e41ea4e4cca14196973ac9bf43c623a35171b621c51ecc2` |
| [`morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed9.json`](../morphogenesis/experiments/E09_pond/placement_patches/placement_patches_majority_seed9.json) | other | 169380 | `6979ccace99e08899732adfabe137aa9cd1edad541c3004774fe16668b441e2b` |
| [`morphogenesis/experiments/E09_pond/placement_patches_matrix.json`](../morphogenesis/experiments/E09_pond/placement_patches_matrix.json) | other | 12975 | `4763142e2f5d752721d010cb9798a2a0911c672149ee419647db122ee638f2fd` |
| [`morphogenesis/experiments/E09_pond/pond_ab_p09.json`](../morphogenesis/experiments/E09_pond/pond_ab_p09.json) | other | 119836 | `ea194eecdeeb0317ee951e643f4bdd18a3b279e5fa446aa7ed65eaee18278a67` |
| [`morphogenesis/experiments/E09_pond/pond_ab_p10.json`](../morphogenesis/experiments/E09_pond/pond_ab_p10.json) | other | 120776 | `26802a06a65094a2545c216722e74bc62e4d9b18c2cbec72d5619ed8c23bb4cc` |
| [`morphogenesis/experiments/E09_pond/pond_v01b.json`](../morphogenesis/experiments/E09_pond/pond_v01b.json) | other | 245551 | `51d09eddfff0d4163b0640858e87ad07ed3e6e191b3a334a07fc4055e8be86e4` |
| [`morphogenesis/experiments/E09_pond/pond_v02_gradient.json`](../morphogenesis/experiments/E09_pond/pond_v02_gradient.json) | other | 203645 | `509bf116c2c405fc62aa69372e3e50174503e08840b5c28c1199755c615d0087` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_inherit_seed1.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_inherit_seed1.json) | other | 127365 | `e5d1ec2ccb01f2b6890bd023a2ff5d675531634ac1909376b1562999558b2396` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_inherit_seed2.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_inherit_seed2.json) | other | 127403 | `c1f9be21b07a85329ee26ffcd2fb4cfbc2009f07a47f9c16fc3e347273f1f773` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_inherit_seed3.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_inherit_seed3.json) | other | 127046 | `f66313a9758aac33c81f0425c4d9ce27034331b3a555453ae53bcf42df4ce07a` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_random_seed1.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_random_seed1.json) | other | 128800 | `160708518d5311d68d1ec751a0e3f55702d1fb5c99465bd9e58be81e7a6b8f7e` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_random_seed2.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_random_seed2.json) | other | 129066 | `d033fabf4cf916c72ebf45470bf46703c1285b2eb271e47cfa23f787703e6485` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_random_seed3.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv2_fd0_BinvA_random_seed3.json) | other | 128293 | `b4a02add9235a6169b0af3e89d897321aa328fe7699f7d2798bc33a1d62ccc81` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed1.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed1.json) | other | 131097 | `d10398e4d2f5e52051ae53d99ad70f57f41be87d1bd8648b4f99b457aeb6660c` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed2.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed2.json) | other | 130815 | `21e574f9124c234b9c8bb119c2c217dd5444656e1e46d8ab574cef07d5014d64` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed3.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed3.json) | other | 130433 | `208d04d52484d55c8b7abb5f4ace02aeb22483172cc96d397c885a48387dd5d0` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed4.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed4.json) | other | 131082 | `67f596f0fd256c454ae169f352456a0b293f3a4f9126e22d88d4b3ea090d0858` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed5.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed5.json) | other | 130617 | `087bbc7bccfdc288529c63b64f7689c62a8460e5c26a87df36776cedc1fdab22` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed6.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed6.json) | other | 130896 | `6a3e7d459d0655996d3499b9f0bd3f87c45fb5cc039009e731056b0422987b7c` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed7.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed7.json) | other | 178377 | `8ea375641cbe255ebca9e77a5d37be2c97df6f52f3c2bc22f5cc7b5bc67c1f05` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed8.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n1_seed8.json) | other | 185284 | `984b45fa0168f3527666269390bcc667c00361a14c6e5242a767cdc3512444e7` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n2_seed10.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n2_seed10.json) | other | 166684 | `8ed7523e244916b5efe4a235669cba93605f4a80f98fb602484e4332416eaf20` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n2_seed6.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n2_seed6.json) | other | 161135 | `f344167e364440e3d8ef9916812e871160c56f26a98647dfa3dbc2581336ecaa` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n2_seed7.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n2_seed7.json) | other | 161787 | `8ee2694e13bbee2ce8e2a95d3ec0edfb8179b9d111b02f4c5104ce83a4867da0` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n2_seed8.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n2_seed8.json) | other | 166325 | `311b13663945e2c0b2ec8412377af45fada18f48a782672bff5d9c42600e25ab` |
| [`morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n2_seed9.json`](../morphogenesis/experiments/E09_pond/quarantine/colinv4_fd10_AinvB_inherit_n2_seed9.json) | other | 166492 | `b7bfdf202f0c0c2fc56e217a7e1a4426aeb1398f089c21d07d9e1b32d5c4ddc7` |
| [`morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed10_notempty.json`](../morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed10_notempty.json) | other | 166993 | `d3e0ad56e0b16487f685bcd9bcea0aead168fecec047f1866a655c51896c5ef5` |
| [`morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed1_selfignite.json`](../morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed1_selfignite.json) | other | 163612 | `a56585d6a68dcd9c3b23721e5c7f7b20ea7a126fa885e1dd75d3d809e6697660` |
| [`morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed2_selfignite.json`](../morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed2_selfignite.json) | other | 143440 | `b1ca59485563ad6ef0959ee939cd4b3925f630f6fb225cb44b2686ddd41f7dae` |
| [`morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed3_selfignite.json`](../morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed3_selfignite.json) | other | 144749 | `5acf87dc1aa45c2eec6e05af3ecb401cae509134d5d596ef8890e363fc042e1a` |
| [`morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed4_selfignite.json`](../morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed4_selfignite.json) | other | 125107 | `e76ca3793a23843cd2c1d068e41426809ec1f3e3c1983648806957832bc0a5db` |
| [`morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed5_selfignite.json`](../morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed5_selfignite.json) | other | 125130 | `47b32e3f181ba6764959db93a979becca73f49dd200fc3ddc572608416342688` |
| [`morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed6_selfignite.json`](../morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed6_selfignite.json) | other | 164193 | `beefcbec7839056f43fbe8073c0730c7116438ecf00ac6c912a74c7000d31a6f` |
| [`morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed7_notempty.json`](../morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed7_notempty.json) | other | 166976 | `168c7103f4bef8c3723df0ecf99a42c931ba119c6c5cc8626d1c2fe79cbbf18b` |
| [`morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed8_notempty.json`](../morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed8_notempty.json) | other | 166932 | `ba019a8c834c08a50ea3c1c6caae626829f7197d60a2199f7209680f81f4e770` |
| [`morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed9_notempty.json`](../morphogenesis/experiments/E09_pond/quarantine/v8_resident_free_seed9_notempty.json) | other | 166674 | `6654aa8ceceb058b7f8982b84a5fe92abc86431b7f40fa9bab43bee14e07fa37` |
| [`morphogenesis/experiments/E09_pond/richfield/bpool_keep_seed1.json`](../morphogenesis/experiments/E09_pond/richfield/bpool_keep_seed1.json) | other | 169911 | `20946327b5bf83b8917cf4bba0e47c5aede6a67507ffd147deafef8cd9e5f154` |
| [`morphogenesis/experiments/E09_pond/richfield/fd0_into_gap_majority_seed1.json`](../morphogenesis/experiments/E09_pond/richfield/fd0_into_gap_majority_seed1.json) | other | 169262 | `6401172504c60dce864d78543f3fd63787a5ce56e4b41ad40f94563bce771696` |
| [`morphogenesis/experiments/E09_pond/richfield/fd0_into_resident_majority_seed1.json`](../morphogenesis/experiments/E09_pond/richfield/fd0_into_resident_majority_seed1.json) | other | 169134 | `c63d1a0e045a8947e03db1d22a67f4e6cf580ed6ca1608c762a41f0526b5135b` |
| [`morphogenesis/experiments/E09_pond/richfield/rich_pilot_normal.json`](../morphogenesis/experiments/E09_pond/richfield/rich_pilot_normal.json) | other | 169176 | `8a58d3981bb4e7a5adba8e56814f0d0ed532bc9e377e7995f40d017937f64699` |
| [`morphogenesis/experiments/E09_pond/richfield/rich_pilot_regen0_3.json`](../morphogenesis/experiments/E09_pond/richfield/rich_pilot_regen0_3.json) | other | 169353 | `54dba5ddec6d25ab6353a228dac0479b44db4b55f8675da7e38d0c84a65bbbf1` |
| [`morphogenesis/experiments/E09_pond/richfield/rich_pilot_regen0_6.json`](../morphogenesis/experiments/E09_pond/richfield/rich_pilot_regen0_6.json) | other | 168861 | `eb62ed1d2be95b734d66300e9e9decaa8fabfb7e993ad0210f9cfffcd91ea89f` |
| [`morphogenesis/experiments/E09_pond/richfield/rich_pilot_regen1_0.json`](../morphogenesis/experiments/E09_pond/richfield/rich_pilot_regen1_0.json) | other | 164281 | `dff6d5b5aa50cd1dc3eb2830a205fbfc0090756d4c64704bdca38318b96f4273` |
| [`morphogenesis/experiments/E09_pond/richfield/rich_pilot_rich.json`](../morphogenesis/experiments/E09_pond/richfield/rich_pilot_rich.json) | other | 169250 | `c6ea0218047012517c9b7d386c521d4dc37fd2a33d885b306644283d8da2107b` |
| [`morphogenesis/experiments/E09_pond/seed_replication.json`](../morphogenesis/experiments/E09_pond/seed_replication.json) | other | 61188 | `169ada0f78afbf386195781512117ce1552a28850773b65b6d310d2eb122b17e` |
| [`morphogenesis/experiments/E09_pond/sel_eps00_seed1.json`](../morphogenesis/experiments/E09_pond/sel_eps00_seed1.json) | other | 481086 | `0644afa43f842e7c1a3dc1cc5bfcd94a06f754b08b35511c240aa5101d7c38b6` |
| [`morphogenesis/experiments/E09_pond/sel_eps00_seed2.json`](../morphogenesis/experiments/E09_pond/sel_eps00_seed2.json) | other | 468098 | `4d1da28190f00667b6251d50e6ead3525f16f5a80c47877afc97b2378176831c` |
| [`morphogenesis/experiments/E09_pond/sel_eps00_seed3.json`](../morphogenesis/experiments/E09_pond/sel_eps00_seed3.json) | other | 477211 | `eb4a8736b0f62fa85bda0a6ddb5fdaf78c66de21c4ee0efa9b65d14c75d6220e` |
| [`morphogenesis/experiments/E09_pond/sel_eps200_seed1.json`](../morphogenesis/experiments/E09_pond/sel_eps200_seed1.json) | other | 478401 | `a72616e445067f3816732e565d134335d35c202955291e70af941214bdcd199a` |
| [`morphogenesis/experiments/E09_pond/selection_matrix.json`](../morphogenesis/experiments/E09_pond/selection_matrix.json) | other | 6468 | `e7697cf9cd686fd0f7af4d1fd92005d429c61aeafffaf238b17be5ea939ee9e3` |
| [`morphogenesis/experiments/E09_pond/sense_noise_matrix.json`](../morphogenesis/experiments/E09_pond/sense_noise_matrix.json) | other | 16959 | `c7e676a74d49332fd81b6ecbbea141df1299bd5bb2768293323bb9e0c65abc61` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed1.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed1.json) | other | 167506 | `082cde4bffe7d7d3393b83a9bfafea75f5c60cf432abe8f5fd78c44607897429` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed10.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed10.json) | other | 166994 | `cc509ada43a2ff80c3295bf05122b888624fd35b10386d620c06837574190905` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed2.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed2.json) | other | 167204 | `593009b84756e4c623afd954dc93add3469b8cec15f4b9a025edfd6c963465e1` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed3.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed3.json) | other | 166870 | `f9fd3cdc8003d0d662f75c80aec52d12e8b41f1eff6cf0972e5cf99d116799be` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed4.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed4.json) | other | 167363 | `79746dab3145d3404ddaac6a21c28a60d316de617c0bd59360b9d276ca231c08` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed5.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed5.json) | other | 166997 | `8211dfe8f0db07a3a483be5518e0a21530326c7de52f8daa5ccc0eb8da9fb532` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed6.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed6.json) | other | 167219 | `771dab3886d6d169003026e7747d5ccde8ec4cdd4cdb02fa52760f6472121554` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed7.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed7.json) | other | 166976 | `7e9ecbdc58e554b5a5770abe4fe1a7193281f828f8b9528c58d7f61ce88acc87` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed8.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed8.json) | other | 166933 | `bf1c9377a029bd148ee83c18d3b541a71ea0b4d2592ee48f262b2a54df77b599` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed9.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_majority_seed9.json) | other | 166676 | `6ebe871ec5bf6fca253f3b3b418abe59a55928331dc5469d7351fe638423bff7` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed1.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed1.json) | other | 167511 | `e30167e4250f42a9ab907900e1a5f29b1f873505377fa91cb9bfe9f73366b676` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed10.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed10.json) | other | 167000 | `7eb36595d469fed89a422afee40812147d481eea11a60b7af6c8b3c8c04500d1` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed2.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed2.json) | other | 167209 | `f9d0b5ce087cdc3f0b7cbb63935f2106cc779fec5d0d153c7b23c1d053fe691f` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed3.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed3.json) | other | 166876 | `f89c7dc531ab1fd45c2cf326f9767341c221d075833cd70f0be80f13f2a8fbea` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed4.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed4.json) | other | 167368 | `3cd94c26e79f0e83ed3e2689009805902797e7e351bd8cf46a7f50a955896182` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed5.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed5.json) | other | 167002 | `8875ff1681d2f41c24aa847af89c0583960233952cfab6a910ea2040464e9824` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed6.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed6.json) | other | 167223 | `a839fec58670e87253d6c703275fcc290a1994c17c7d5fed09b3961ca590f8a4` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed7.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed7.json) | other | 166981 | `60fbec1d4940868e929c4969d252b2e7799b77d5581b220ee6185fc4e80c745a` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed8.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed8.json) | other | 166938 | `45574d07b875dbe349f412ccd513cbe9346699f531e9122cffb2195e0d7319bc` |
| [`morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed9.json`](../morphogenesis/experiments/E09_pond/v8_into_gap_weighted_seed9.json) | other | 166681 | `38f69fca41e7e74f2f93571655eee8056b41d0577a83a448667852107f5ce2b0` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed1.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed1.json) | other | 167241 | `dc4544cc7e7ef25db46fd36c1ba2bc8530cc18e764551e686c41eeb42c2d1aa9` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed10.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed10.json) | other | 166936 | `f99f038b23d4a8cc35d888b1f9d2721e0dff9df001c65b1d0d9e83ace413b9cb` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed2.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed2.json) | other | 166534 | `3ae808291f8109e12146d446f9408e03958fc614be676712230faf5425fafa5b` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed3.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed3.json) | other | 166697 | `08796f4ba3c4cc7cb2f9c986cfb66b9e9d6b4c949ed39114b1723301581f4e95` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed4.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed4.json) | other | 167339 | `03d8705565ecf2a292a90c3b33c6eda8c7e2fc86e452cd81ea95daae932c03b6` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed5.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed5.json) | other | 166943 | `c3395bc59ca6519f25a924551939bd16364d347ad2d626c80efb461a66b76a4b` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed6.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed6.json) | other | 167182 | `ca4d044a349ead372984ae54cd9591b6ac5d6f4c9891710d60a4cad3d4a47065` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed7.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed7.json) | other | 167197 | `824c7d080f64cf0e599acc3e29e4c8a8e35601db8ddc5f852647376a4ddc8456` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed8.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed8.json) | other | 166802 | `22e68b74f2a5acfa75c01e0f4797230e717aff6cabdd2b1515ba1dd1b0b347c0` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed9.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_majority_seed9.json) | other | 166744 | `ddc47e529e0e581b8d83bb866af62cbe35c6c72832a407f5acb6b5429a0d783d` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed1.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed1.json) | other | 167246 | `4cd4f3840b968299eb3f0e32921a2514331cc7f2cdf003f687c63b717a760b9f` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed10.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed10.json) | other | 166941 | `5cf708bdf7b7565f0547a5dc71e1259e82c4637c5834cd94344cc682cc64f7b2` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed2.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed2.json) | other | 166539 | `99e1a332de9fff4f968cd3337bd7339a14fba63c62bca2129b347b72ec8759dc` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed3.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed3.json) | other | 166703 | `b4adc65dd53b0aadf4e86043ef57418330fb89701c6b71c80ee7eb91f1ed79ac` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed4.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed4.json) | other | 167344 | `71c12551d553ecd8d0a818f94e89d0ad9d658373b76babbb445f112d6447766b` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed5.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed5.json) | other | 166948 | `f3bd398ffbf3c16c6fc1796b692ab95a61f30f14c2a8ea5c122186c2759a31e1` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed6.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed6.json) | other | 167188 | `71ffbb5407933c4404f27a87fc0709195f7cb0a32582deaf5264bd8a2fb7763e` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed7.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed7.json) | other | 167202 | `1a907f25477c42756e6f56928a9a57a8f4f4ea8ba85a61fd1b45f390b8753a85` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed8.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed8.json) | other | 166807 | `413cada363b91f548a135ea1b8460a1a7ee1114c5d4c7adb1c18978b34e34c84` |
| [`morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed9.json`](../morphogenesis/experiments/E09_pond/v8_into_resident_weighted_seed9.json) | other | 166749 | `b07d29e2aeaedd4fc21364de3be25f0671b5c2bd9bad1b4b2b9d3e2ca003eb04` |
| [`morphogenesis/experiments/E09_pond/v8_matrix.json`](../morphogenesis/experiments/E09_pond/v8_matrix.json) | other | 40724 | `2cf3ad9b5fa4b783fb70f8fcd2fd1d322e48f67122021e3dbef7a22aed590040` |
| [`morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed1.json`](../morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed1.json) | other | 167478 | `6fcaf0d1cb51dc45c78112e67d65550b12990667a4eb884bce58865caefb7bea` |
| [`morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed10.json`](../morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed10.json) | other | 167010 | `ab591ee0d088d37b83f3567563cc16540a54ca2de04760c53edc24249b7698b0` |
| [`morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed2.json`](../morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed2.json) | other | 167067 | `68d7cb331ec1f3a14b380d075cea1ecbce19bd5f6caf8605c64a7aa1bacfd90b` |
| [`morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed3.json`](../morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed3.json) | other | 166806 | `f05bc4fa57ce87c717d02cabd3cb118007d089c182ee1b5e5e1e18658ee852b2` |
| [`morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed4.json`](../morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed4.json) | other | 167368 | `ff6a03ff00c2bfead8a7a2da9970d6d34367476c44a5c1eb5b7a91883fb9b4b1` |
| [`morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed5.json`](../morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed5.json) | other | 167092 | `074ff6cbd29bac03da285d7fdddc7fc75a67a493a6a8a57c3372bd514477538e` |
| [`morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed6.json`](../morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed6.json) | other | 167160 | `9b119d1b0d3840c02d9b7e140593949f714a571ae48121f488190f1e513727a9` |
| [`morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed7.json`](../morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed7.json) | other | 167264 | `73e6906acfb352e89d3cc49a21cbd6a87b04cb140b75a6a1c443a981a72fa41f` |
| [`morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed8.json`](../morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed8.json) | other | 166758 | `0f4f29d55050d5be1640fa896c441aaf169d4b68312b374d4ddd6f0a0627ee48` |
| [`morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed9.json`](../morphogenesis/experiments/E09_pond/v8_propagule20_gap_weighted_seed9.json) | other | 166572 | `30741718139b1380344c7036176c06b5c78b376e1240b65981eefb02ef350bea` |
| [`morphogenesis/experiments/E09_pond/v8res_into_gap_majority.json`](../morphogenesis/experiments/E09_pond/v8res_into_gap_majority.json) | other | 169535 | `bada0ef36cba73e2c863467f24857fa2be6999a0806df2feb2f7f85605d0ed55` |
| [`morphogenesis/experiments/E09_pond/v8res_into_gap_majority_seed2.json`](../morphogenesis/experiments/E09_pond/v8res_into_gap_majority_seed2.json) | other | 168274 | `754c4080f7e9b1a651a927d2785d631a5d073deba94f2a83517080fafc658c0b` |
| [`morphogenesis/experiments/E09_pond/v8res_into_gap_majority_seed3.json`](../morphogenesis/experiments/E09_pond/v8res_into_gap_majority_seed3.json) | other | 168773 | `707801a8801976ca23d14ea0627c17e680bb3b7b582fe5b05449f2cff6175696` |
| [`morphogenesis/experiments/E09_pond/v8res_into_gap_weighted.json`](../morphogenesis/experiments/E09_pond/v8res_into_gap_weighted.json) | other | 169300 | `1f6d53b139ec45e3303aebc8d5639a170dcee2f13f3d8563f63667da74d61487` |
| [`morphogenesis/experiments/E09_pond/v8res_into_gap_weighted_seed2.json`](../morphogenesis/experiments/E09_pond/v8res_into_gap_weighted_seed2.json) | other | 169097 | `132822e8b0864a83600ca33dac564e7dd80b472dc97586607642b343f812d18a` |
| [`morphogenesis/experiments/E09_pond/v8res_into_gap_weighted_seed3.json`](../morphogenesis/experiments/E09_pond/v8res_into_gap_weighted_seed3.json) | other | 168692 | `542305468df27c6426b79becfbf504aa711a350607d5cc73487482eae2269c5e` |
| [`morphogenesis/experiments/E09_pond/v8res_into_resident_majority.json`](../morphogenesis/experiments/E09_pond/v8res_into_resident_majority.json) | other | 169222 | `9dcb6eb86dc77a8f7c87135d03c848cf6e9efad7255531e3c95f227bd99c5d6b` |
| [`morphogenesis/experiments/E09_pond/v8res_into_resident_majority_seed2.json`](../morphogenesis/experiments/E09_pond/v8res_into_resident_majority_seed2.json) | other | 169063 | `0cfa84358d16461d5fc2efd08cc12b7cf4efef35a6749e5ddd92d6a56654b549` |
| [`morphogenesis/experiments/E09_pond/v8res_into_resident_majority_seed3.json`](../morphogenesis/experiments/E09_pond/v8res_into_resident_majority_seed3.json) | other | 168551 | `5ecffd7f9ead7b3b0c1d9163d6b9e7d2a3202c9e6f2323cffff1baf3230fb6db` |
| [`morphogenesis/experiments/E09_pond/v8res_into_resident_weighted.json`](../morphogenesis/experiments/E09_pond/v8res_into_resident_weighted.json) | other | 169228 | `509fcf315340cf57571a98f1e5105103d9e808677ef918d760ee62bd8daa1973` |
| [`morphogenesis/experiments/E09_pond/v8res_into_resident_weighted_seed2.json`](../morphogenesis/experiments/E09_pond/v8res_into_resident_weighted_seed2.json) | other | 169068 | `98aafa2d8e2068e012c21ea53fdee66e9062aff173a35cd73884999ab0aba410` |
| [`morphogenesis/experiments/E09_pond/v8res_into_resident_weighted_seed3.json`](../morphogenesis/experiments/E09_pond/v8res_into_resident_weighted_seed3.json) | other | 168505 | `3181208f76758116149052dd70c4b75699c50843edcd1eb408bcc0d251f77cdf` |
| [`morphogenesis/experiments/E09_pond/v8res_propagule20_gap_weighted.json`](../morphogenesis/experiments/E09_pond/v8res_propagule20_gap_weighted.json) | other | 169336 | `b5fbd164cccff6ad79aa7f0ef9f6ff3ae5b2df88ef1974d52c009ff178ff8a88` |
| [`morphogenesis/experiments/E09_pond/v8res_propagule20_gap_weighted_seed2.json`](../morphogenesis/experiments/E09_pond/v8res_propagule20_gap_weighted_seed2.json) | other | 168973 | `356ed2185961567dbc865866adc01d9081e991ac223231c826d71741564fd570` |
| [`morphogenesis/experiments/E09_pond/v8res_propagule20_gap_weighted_seed3.json`](../morphogenesis/experiments/E09_pond/v8res_propagule20_gap_weighted_seed3.json) | other | 168720 | `e0a01a6d55f4d9d57c8295ae6448ac27114e94904365e3098fd9879e3cbcc1f5` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche2_pilot_depleted_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche2_pilot_depleted_seed1.json) | other | 222584 | `e000dbeb9cdb0cec46e9567c7cc174b0fe7d3c4412295f226a0976da390e3cb5` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche2_pilot_legacy_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche2_pilot_legacy_seed1.json) | other | 223897 | `4b5505d66496ea9e83fbad99565b55ad45e9502338f737e02bb8b29a9ae57526` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche2_pilot_prepared_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche2_pilot_prepared_seed1.json) | other | 227958 | `62277c428de2eb402fc152e61e0eb3e9ea9b24b172814fb384ba1a04a243d25b` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche3_pilot_foreign_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche3_pilot_foreign_seed1.json) | other | 228971 | `2e8db6114882708886c8acc5fee68a9f9621eac40d92b21510c92c2182dcdd66` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche3_pilot_legacy_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche3_pilot_legacy_seed1.json) | other | 223897 | `2e0ab2758778aa74dd33b0d17da2351e00875bcb2db50bc3b57fb769ba1c4002` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche3_pilot_prepared_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche3_pilot_prepared_seed1.json) | other | 227958 | `455d0c866b4c482f7172e7e4c79defd1ce8d57748ca2667c35bf6c8500a38048` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_density_matched_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_density_matched_seed1.json) | other | 229757 | `bbf3170c40a8b727bc3af609fb13133d27093ca1a61f7bac4ccc059693e47ef1` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_density_matched_seed2.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_density_matched_seed2.json) | other | 235666 | `fe64e71b57b152e0fe4bbf9ff3550b07fe2f220daa1d25d8f4783f6aa36aaabd` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_density_matched_seed3.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_density_matched_seed3.json) | other | 236645 | `216ff49b4e92aec42b5cfec26c4726843eaaa18bca2c689f5249f601a524a89e` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_foreign_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_foreign_seed1.json) | other | 228971 | `5b6cf440d2a2c437ac7aee543cbc30d0f222995d996cd1410489de3174a15266` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_foreign_seed2.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_foreign_seed2.json) | other | 234821 | `0025eb42e3769f532a281f3d2c7b81c0783d85c94e1378fe49e565d85f6d0794` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_foreign_seed3.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_foreign_seed3.json) | other | 229346 | `9d5e98d68e1a31040e35b3158cf8ebb09226838f49f340126620b47dc4573282` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_legacy_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_legacy_seed1.json) | other | 223897 | `b1c7395a2570c6572d1afef75b9fb16f43b3fadb622d089ad2a99dca8d92257a` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_legacy_seed2.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_legacy_seed2.json) | other | 228529 | `f1a2e1d3e4416d1f9e59aaa02d88ae0a7891d118ec6aee3c6ae5f3964bbc8479` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_legacy_seed3.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_legacy_seed3.json) | other | 229332 | `135503cc4d12ceac046b5e412a62316f9ca1bc24c905827b36b1d9c5b129c56b` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_prepared_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_prepared_seed1.json) | other | 227957 | `185051b7e0199012a65cbfa04b73fb8890f41a4fb22137ed37e6675534b56618` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_prepared_seed2.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_prepared_seed2.json) | other | 235285 | `818ac9d8d8697e809d851ec2a814b752eda47e93c3751afb61e75ee9fe91bca6` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche4_prepared_seed3.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche4_prepared_seed3.json) | other | 227250 | `5391945bfde1da7f48b050c419eb417327880520e57ea864c6945b413f41acfb` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed1.json) | other | 225898 | `b1e6aeafdf32cfa1f8609877c37e1d59545322f54e1c7959debea8690f8a9216` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed10.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed10.json) | other | 234492 | `14571bc4f92b8b6aa6fafdd9f80d47da1f1eee492c08b59703171a9443bc80c9` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed2.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed2.json) | other | 228604 | `40363a6e7e8c0765d45558948c412d1d4c8fc5e62d532245c801ee5a003d4384` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed3.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed3.json) | other | 220381 | `60204782192db79c20cc0f7bbcb76f2d9b2f97536fb7486f1a170ca1db612bae` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed4.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed4.json) | other | 230252 | `52c406b51c02fdaa256123aacdb809d7632befc04d4de8c933b7e16f8da644f9` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed5.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed5.json) | other | 227851 | `f9923b8760afc4f80da98c0da8fee0897fd18ed060d519d4091c9aaeb1edf134` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed6.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed6.json) | other | 234964 | `ca84fab5d8780b5938cf309acb8012f794f875df7a662007bb77e0e5fb1b4258` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed7.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed7.json) | other | 232051 | `0d1a8642669568ce0046a3d97df7e4727e15ba96fc614e0bf5a8b8b13556989b` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed8.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed8.json) | other | 228140 | `3ace6afc1373a925c2d53d89da35c75f33d6f291f562628f4d6de89373a8460c` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed9.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_adjacent_matched_seed9.json) | other | 235489 | `a9740dfdae5073a7b662490cf1a57ba357e08bdf0967089c45b04e85948fa5a4` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed10.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed10.json) | other | 232764 | `93e5e3a4f2091f610d7c58d499f00a152ca36c8dc039a4c29ca130efba5ec941` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed4.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed4.json) | other | 231818 | `6c0d55e7163a05253fa55b34cad5bd2381ac201235d21acdf55d0109b835f917` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed5.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed5.json) | other | 224011 | `92b5e9e1ac391f41059414d2c529666aa19d07874691d58dd7f08974e0bec110` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed6.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed6.json) | other | 238259 | `aafb9f240ecfbdf1b694222969aa2d1b458ff110fb46b0baeb4519fe9b80e053` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed7.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed7.json) | other | 230129 | `a48be79ef18792a89a2ad99a8e0705e45a888becf0eaab98f915d33351f8f510` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed8.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed8.json) | other | 233404 | `87acff3c6297a4ed8aad449bcc357bbc7415fad55bfd7111e137aa5f49a845db` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed9.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_density_matched_seed9.json) | other | 228633 | `19b5722e7e3fd8e130027783f0cffb4b92bddf59e7de188a23ad91929fffd321` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed10.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed10.json) | other | 233810 | `664f2824729c49630ba4f8e4bb66bfba43a9fcaba8eda188b915e74503c50b5f` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed4.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed4.json) | other | 165957 | `056673e4fc0afef80e54709ff530179170c036e312e6bbc4efa8f7c2b877425a` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed5.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed5.json) | other | 237425 | `85f747f5478b81a9895ad7cf350fb631b69019fb70e57f8f8045601343c44ee3` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed6.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed6.json) | other | 230885 | `e416c82dce12cbfe3959c734d28e321e25e26406993bc6b36b667bb8a5035b77` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed7.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed7.json) | other | 230329 | `9404ae782d84efc6f1c967cdb6dd697f9eb0d2ae6c75cf27dc4085e9e6025f2a` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed8.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed8.json) | other | 221381 | `6201bc14a12e2b980f6501d8b8d402f4ee88f524a75dfadf3bd076f60e251aa9` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed9.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_legacy_seed9.json) | other | 228550 | `252f01a71b8d1712360c17998ba488d782423fb487195f943740aabb86678a85` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed10.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed10.json) | other | 228359 | `e0a514afb0102a38dae0235bcaff7324e63f2f7d28053c40460d7f53618652ef` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed4.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed4.json) | other | 229319 | `e01b5a2c2d325961cae943b3860277457808fbd8c10865da1cd710224a2fb1ca` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed5.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed5.json) | other | 236344 | `dfb90ef37b33eecddf529baefae915e0aaab0b57a831cc5fb40a0895b5c844c3` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed6.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed6.json) | other | 240949 | `d806fa435e427e2f5501d8fe733d5fe29b25253a967b8efc26515b7bdd1d1902` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed7.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed7.json) | other | 238622 | `5eba6b66598e7c17cd8be659bc76605f100a8084a6cee1a8aa197ffa908fc53a` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed8.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed8.json) | other | 229105 | `e25bd713cdbdd05123e56c9b5ab7a0af7e6965f95c8ea5f07005cf9a36a61f0a` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed9.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche5_prepared_seed9.json) | other | 235734 | `1d83868540379164cb366c13e3ff68d97c95e377a905ee1fb8121452be2415d9` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed1.json) | other | 236604 | `cbf1b4e9ab0301e593fd6824621a2570ec5b273526701427cdd04db198a0ff9f` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed10.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed10.json) | other | 236494 | `83065dfe78bb12f02f95db33e4665efc9fcb006c7cc69ef9a674c68ad2525212` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed2.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed2.json) | other | 239606 | `7f3734a3b31e1f2f72507c18bd2b0cd03cb15835520e5a113a9118f721674fc3` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed3.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed3.json) | other | 233017 | `e77c709bd43a5f4bf5a0ccce92bd89e8b064acbb71af039f79ed639f6d3747e7` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed4.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed4.json) | other | 166587 | `96b2c057459645c7ab296af67e217dbe26dedc45ae1754541f06a390a947db1b` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed5.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed5.json) | other | 228584 | `85514609ead0bb8ac157428727bb4bab60d6507f418366edfa0d4599e2585f7c` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed6.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed6.json) | other | 234070 | `14220cf66781db76924469de6018ea1358e9f97988d7d101f7ebdff090f273d7` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed7.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed7.json) | other | 225746 | `0b2f651cffb94be437a662ff3d8721fe3d9487b9d0c1c1b2a1c290293df6505a` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed8.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed8.json) | other | 232310 | `cfec4a49e008d386d5a578d8d34f85adc96e3bd725ee8f81e41a616cb17a96fc` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed9.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche6_adjacency_exact_seed9.json) | other | 234410 | `084124f874d0eb698fb9519910c1e2dea98cdadb38c86b575a3e126c320f601a` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche_pilot_depleted_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche_pilot_depleted_seed1.json) | other | 170061 | `9d9ff49b927777589b45adcc3c0d1eb3d68b2f9e8474f74258735b218eb95681` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche_pilot_legacy_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche_pilot_legacy_seed1.json) | other | 170597 | `cad8c94b6bb2e60eba3905be21e430beae606da2f0369cf74b3e25c51a4ec039` |
| [`morphogenesis/experiments/E09_pond/w1niche/w1niche_pilot_prepared_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche/w1niche_pilot_prepared_seed1.json) | other | 170402 | `62bc30529e66bee00d1cb3360fab4f9129f0cfc8de830b6bf96c22d6e0709d78` |
| [`morphogenesis/experiments/E09_pond/w1niche5_matrix.json`](../morphogenesis/experiments/E09_pond/w1niche5_matrix.json) | other | 26989 | `3900c11836c62718cfa7ec7e521d59cf5bb4ceb46154667e4f3bf8fef00d6f66` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/eq2_legacy_seed5_1807898081.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/eq2_legacy_seed5_1807898081.json) | other | 239455 | `3208a499ac3410d56535ed448cb2a05588de456737f52ba56718a0661e8c6363` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/eq2_legacy_seed5_605075221.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/eq2_legacy_seed5_605075221.json) | other | 239455 | `5200d3ad229051c69db48cf1cf7adf2b5d10793db7b6cbefad4a03b827ea26e7` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/eq_legacy_seed1_head.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/eq_legacy_seed1_head.json) | other | 248100 | `ba5be8063b9daf961e3ae825efe6c83350b8a6f20b121eb51c456045b1e65c21` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/eq_legacy_seed5_head.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/eq_legacy_seed5_head.json) | other | 239456 | `10d649a124d72e92f77e8ac58aa639723b0235d1f08229380ec92f48ec35dbba` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed1.json) | other | 236885 | `5c32293569f4627f932a9fca7676165bf1e1914bc10a9398f40bc301e15d8876` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed10.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed10.json) | other | 236741 | `4121cef79ba5efc48f8120c94ebf9fcfd92b329f9b1c400f46ecb71f4a500afc` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed2.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed2.json) | other | 239886 | `251b14ae504e7553ee8a27fa505312cfb1f4d41adbb92ca982f247b7b0951ded` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed3.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed3.json) | other | 233298 | `d397e45056147f259ffb14ef537f54599b1a87a68d927c0083847da0322d0f31` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed4.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed4.json) | other | 166869 | `1c7c0df85417403b44e6451fefeb0da4e1bb1609136d0156ac8f3d9d383bd7af` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed5.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed5.json) | other | 228864 | `6b992495a398b04c285d8be2fd28ec16c92736b6e3c8d38a4c3b0618051b04d6` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed6.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed6.json) | other | 234352 | `e9fc8fe1db954d4be61a61f455cb7cbd0dac44bf63a17e5a0446a6f4d699f631` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed7.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed7.json) | other | 225993 | `c537d28068d9b4e4b2d61ddd5e516ce61cb343887a8af66d8d0822d79e9ce5a9` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed8.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed8.json) | other | 232557 | `1219c9d957cb9b41a3f52808fe73361599ec02aede229c2ad21190609eee28e8` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed9.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_adjacency_exact_seed9.json) | other | 234657 | `005d99b97b1e3a503ce562d1af418822321e4b4c2fe2ca419029e8093cc513d9` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed1.json) | other | 248100 | `904916dc8b0bef42b802096177e24562369416e660a5a9b21ad41f84120e7645` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed10.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed10.json) | other | 234090 | `065877cae2366b81f5525e97e67d982bf6bda2a93c97eab7e6b8ecac2c1182df` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed2.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed2.json) | other | 228809 | `99181e6adfb62e79f4c1edb9b7054f2dcba6a2208b48f8dfd456d2eb8131ae1a` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed3.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed3.json) | other | 229612 | `378d9b8e091cd9ecf3d6c64b4eff785145baa31932f11a7a838bdb7a00570603` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed4.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed4.json) | other | 244891 | `0714f48a2f755c91c2580e45e6a678b8f20904404b048bfc023202be810593b6` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed4_OLDARGS.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed4_OLDARGS.json) | other | 244890 | `c218217aa02fb54033e384042a142f3569f7d4bb7c6fe505cbdcd0f88910cd84` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed5.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed5.json) | other | 237705 | `76130546d21b64c01fe871930c483d97c45adf74899a87d6b38fc36656423571` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed6.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed6.json) | other | 231165 | `c79c932a307dc0c6a0fda8ca5a170b38d956558c50ccf0103a7a87d725f7c127` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed7.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed7.json) | other | 230609 | `a0badfec462a114073aefc2cda58761b83a862571e8487215202620525b90a3c` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed8.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed8.json) | other | 221661 | `e85db09497058960d7c744fd4a74c653d5a7c7f813592a337badf769f2b5166f` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed9.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/series_v1_mixed/w1nichefree_legacy_seed9.json) | other | 228828 | `dc9c2ced1dc93d4d37936ccf26d3719f3f4e6b2c2c73244c2a7e0883f3193993` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/w1nichefree_legacy_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/w1nichefree_legacy_seed1.json) | other | 248100 | `f985b91be64753eaac5c72a370d74bb255afe8abed9f4777bc26667c44ca0bd2` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/w1nichefree_legacy_seed2.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/w1nichefree_legacy_seed2.json) | other | 244574 | `8d3548ec89fd8fb98e4078efe24a7bb986b9bf095c64478175e8b841790a53f0` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/prequel/w1nichefree_legacy_seed3.json`](../morphogenesis/experiments/E09_pond/w1niche_free/prequel/w1nichefree_legacy_seed3.json) | other | 230507 | `eee17660fd7eda78a2c2d78ea01285cd37c185d0e664e3df3fcca1592fcfaf56` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed1.json) | other | 239087 | `227c2e7292752379091870a3d58f657983a1dc8130a03d8c27bd413a0a726288` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed10.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed10.json) | other | 243209 | `c7435da1884334f3eb6cfb5ec97576af53e131c91455505e719faa45d781c1fb` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed2.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed2.json) | other | 248055 | `3b05f50b9d7dabeb83ace4e032259d68b9243329d604255a33559c6037763fb8` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed3.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed3.json) | other | 230657 | `fc3e4bdab603474b5a9913117eeee99c10a7a754d9d17f4e55ae19403bcddf2d` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed4.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed4.json) | other | 245561 | `ae865207d2f5714cc6ab2bd491eae839a8fae0cfd6a388fb32d69766ae2a2ce9` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed5.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed5.json) | other | 248573 | `4e437bacc27eeef69949a3db58192ccc872af4b4fb16a7d0169cb332df49c8b5` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed6.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed6.json) | other | 250384 | `b2bf941fb8e988830016625d6b417b72c552af7405582a9bb645ec753bd4908b` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed7.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed7.json) | other | 234242 | `73d1ed8b71242271b29ac000c1dde447c80af8df3a7a92dcdf256dc023edca4b` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed8.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed8.json) | other | 232991 | `763027ba3bee7c699f47e57aa37c86a6c4d3f04e5546d2539c0679f85aeed6d8` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed9.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_adjacency_exact_seed9.json) | other | 242280 | `6f66afe062c2c6d3cd9ed7ddf92ab35a3a5268677833a6d9d110e4f9597ddb1e` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed1.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed1.json) | other | 248100 | `fe6fc65df93c8f901d16e9c1fa3ab6c8c29d866f2e5d99eddd9ded89a825a1a7` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed10.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed10.json) | other | 243856 | `ce1a93e78467bf645ac955f98b0dbd2b76937cbfb4a242f29201764fca2f71a0` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed2.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed2.json) | other | 244574 | `3364a02ecbde39320b2184d7bed48fc0b7e180444a8e0a5bd2556e338753ecc7` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed3.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed3.json) | other | 230507 | `f76932198dc4b7efd83bcc93fcabcde690eeb93018d6cab57c7007deaf4fe8ba` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed4.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed4.json) | other | 244891 | `0a73d6b773bfae54d0be9bbb19b76b6774e87ec059ef9b19a1a1e238269d796f` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed5.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed5.json) | other | 239456 | `b2b9004efd140982af78c5e59c0f361ef393a04017840e0dd49ceefaa98c75a2` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed6.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed6.json) | other | 249611 | `b8d10e85a3f01e7a68ce42ee4b38d4185975a01d56d3620c34fe81d54f7daffa` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed7.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed7.json) | other | 240235 | `559dd34e775bb7ab3586f848458b311e9e521d139df122c6d69a0b9b6db536fd` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed8.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed8.json) | other | 237630 | `58af5d40a70d37dfdd60dc380361bab6f986f3608510eabf7412757c1b9d9031` |
| [`morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed9.json`](../morphogenesis/experiments/E09_pond/w1niche_free/w1nichefree_legacy_seed9.json) | other | 231768 | `59b047a0838972aa46515982592874a10fa7c3207013e02e06b00eaac74d629c` |
| [`morphogenesis/experiments/E09_pond/w1niche_free_matrix.json`](../morphogenesis/experiments/E09_pond/w1niche_free_matrix.json) | other | 13625 | `5d68937ce055d50a6176bee19166080a7dc2dd521576cefb96bb012864f0729c` |
| [`morphogenesis/experiments/E09_pond/w1niche_matrix.json`](../morphogenesis/experiments/E09_pond/w1niche_matrix.json) | other | 35719 | `4ff9f79ce8b5bc357f7e518dbb1851d0c36ffc78b091eb610a45fcc61c9ba065` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed1.json) | other | 492970 | `a69ec32c830a7f8b1783605a6c0afa4d75848df7c390c0c2bdc4461764d73d33` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed10.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed10.json) | other | 479514 | `10559007a777c63c04f469d52f086594638e1306aa043e8035eaa930d0b88995` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed2.json) | other | 489192 | `16a30cd032ac099c2dfda7ec172fc61afcdf89b80e4a78a349c48fcf6718f70e` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed3.json) | other | 476771 | `f37a7aecea749c88f9c95f70759ae4263ee17d518e1402cef0151007016050f2` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed4.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed4.json) | other | 469508 | `161d947c09289b60f4987ea4e9c990506a211a0ef33f782019df5ded4864d039` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed5.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed5.json) | other | 503629 | `c2d4bcae6974ce79abd5d3b6d2ab1a0e94720bf2a35701303c3dea50d7b4f932` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed6.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed6.json) | other | 463682 | `df508ee48878bbb71ae86645a8e663dcc3d842eb763389bae1a55154f5ae96fc` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed7.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed7.json) | other | 471488 | `a3ecc2ae5b178624b78ad59c9cc6879dc108a715cbaf2062c9e4c9e80f6fa9b7` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed8.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed8.json) | other | 473599 | `8098f88e4f5dce2079bb6c4ffdd569959bb2747cb17b3532c5ae990585bd21c8` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed9.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_cell_seed9.json) | other | 479894 | `93b5479dedaa66df48f60844410cda2c484b0b20d776329454cfd044f09f71aa` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed1.json) | other | 482750 | `1a4abf833b7537aa6424a1ac7672f3ee542c751cfd9647c6402272bd5a899e7e` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed10.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed10.json) | other | 483098 | `4c9868220a6758741056de8d83ba366a91e9369265a5eea099484df8ecede795` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed2.json) | other | 475605 | `ea259e94498b3d69a578a122ff6358406321cd300b173de28caa3ce5e118c730` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed3.json) | other | 479956 | `2a7a20511287dfadaaa7444cac9009fdff932bc7e7b3cca8c78818b27d55c8f1` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed4.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed4.json) | other | 500270 | `042c7b85d3d5446dd1120d2b2ba13823d3292dd86bad1b5006e3f69e05de5fa8` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed5.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed5.json) | other | 488932 | `d393223cd6df6e3a9e3f0ffd1f81c878b84a293474e2aec000027739f125e937` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed6.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed6.json) | other | 476403 | `21b70fb4b0e2b4b88bbb289ed79dbfe2550875b781cc9605204e9f25802de85a` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed7.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed7.json) | other | 477597 | `fad0967353fa862b46f297d10242520d19bb46647b9cf10a9df938df02ed656e` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed8.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed8.json) | other | 476239 | `767dc8455a20afedcd3ce94974c9a44128a3bfe8cdbc9fa436d9ceb094b6404c` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed9.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_colony_seed9.json) | other | 473633 | `76e0f36d465d58dc54349c171922ab6e2060f77143c99e656227ab36aa38f421` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_pilot_cell.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_pilot_cell.json) | other | 492971 | `849df045333ecf40149df5872607c17efe28299dd8c58ec3299fc5632ae0e5ec` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_pilot_cell_m10.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_pilot_cell_m10.json) | other | 587674 | `70aa48083424a12a3d673e8030ebb7ec5c74e1b40295e30f5896f00ae83bb2f0` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_pilot_cell_s900.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_pilot_cell_s900.json) | other | 799704 | `87c00d0dde5c733d448bbbd30f91bc791cc107a6a2b9491391e73bf9312462c3` |
| [`morphogenesis/experiments/E09_pond/w2bud/w2bud_pilot_colony.json`](../morphogenesis/experiments/E09_pond/w2bud/w2bud_pilot_colony.json) | other | 482751 | `84337931ccf57fd9f3ac1ed37ac931ba3eefdf480722f132f20f0df5276090d0` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed1.json) | other | 481532 | `945a120c8b37d5e48e8990dfcc6f7b46e4917740e995b7a03013c7dfbe08f372` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed10.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed10.json) | other | 477244 | `55daac272307c5e3a0164544999f764d27a4939855a2bb6e5a506c1ed648337d` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed2.json) | other | 474856 | `ee5d20ef04f4a902dc4db106f07c52d38f33c3bb11516d0734b81c593d759f05` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed3.json) | other | 476862 | `16ab00082f5332d1da70e6810792ad7cfd3c522d40a50aab3030baf94af40b7b` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed4.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed4.json) | other | 478889 | `eef4004dbf2f6baf1168d4754f8235614c03e7405bf635588713f3f0e4aaf374` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed5.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed5.json) | other | 496848 | `51f186479e16ce17b7089d08779d1e07c4cba00689c8aadfcddeddd128d96b40` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed6.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed6.json) | other | 484460 | `dbe19cbd804f3b9b791e08a7fceb49f58a383ad5f3b45908c51ac9c6baa579d8` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed7.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed7.json) | other | 482914 | `cc0920bdb9f4b422c44f150bfa887cec01e531377ebb25aac8037905664b7dd8` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed8.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed8.json) | other | 471413 | `242672e5f4daa4384e9d88e2bab21773f7ecdbd15a6c735c663929ca3b53fda5` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed9.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_cell_seed9.json) | other | 463090 | `91dc2fedb194577936133ae5f2fe997b944a95138e2930309dff9dfc6902b575` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed1.json) | other | 475354 | `ec7caeae292f805cfe7ccde3034c16f803b9f67883c560bcd9cf4659c538e5f6` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed10.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed10.json) | other | 487242 | `75cb1a72cabd062e0d46fb4c0e98eb3e2310808676b1ef54d6ad6e71812b682c` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed2.json) | other | 479728 | `afe708ec267f23398ebd9b0428b0fed8fd531c4337621ba40cc066e814a5ffdf` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed3.json) | other | 476110 | `854a4aae8cb3dc6232189b275576b93aa9d36ad89ad68ae00086a8c492c1ec69` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed4.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed4.json) | other | 488213 | `6893adc50727f2615ded8722e1b3dcbe8275f407d099b6d3ec6c067759836646` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed5.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed5.json) | other | 489933 | `c08c6fc2b437e52b86607b7caeb23ceaa9f920442c5852a29a4866c73caf62a2` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed6.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed6.json) | other | 484627 | `28cb4a9c447a56d680befd63e241d52d7e8a2709622c2e1a4a5ebdcaab29ee0a` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed7.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed7.json) | other | 478843 | `e4498e88999ce51b3353c166d00f7e64a4b0530b44c1e70a6074421b5c1e7b34` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed8.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed8.json) | other | 471019 | `89ace0f2f4b167f53ffab59cb35f9d00a08970c054d894bd9d29235e2c6cce36` |
| [`morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed9.json`](../morphogenesis/experiments/E09_pond/w2bud2/w2bud2_colony_seed9.json) | other | 476790 | `3b08fde526aa6cf8983155f0bc4ed1d87e0d60cc7deda6b8a303b8ed07ae29ec` |
| [`morphogenesis/experiments/E09_pond/w2bud2_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud2_matrix.json) | other | 35568 | `1c0cf283d72cce25f8b6128e2d2f07caba0691c9e4853dacca16a81c51669022` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed1.json) | other | 504706 | `f9e7bd1cbe3103192ce113f209e8add597d162cf03ac9f7f98284367c4a130c3` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed10.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed10.json) | other | 501244 | `e5e30911f359cdb93b04723585d4c74bd4a47e0912306807732311ddaa5ae18c` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed2.json) | other | 497888 | `66dbd45683fc134f8b5bad62b85ea4bf8e14ebb9a95c07a9b8b5d6f392d3fb98` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed3.json) | other | 500350 | `2986bef6a0dfa299bf5b5e8616ac01766283002e769ee80c704438c2e1a68767` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed4.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed4.json) | other | 503175 | `c65741897900b2a407c1a900d4ac8f260549bc17a3580381df65769bd5aef04f` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed5.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed5.json) | other | 522872 | `9348e26eb6082fa65a784538e887924beb5faec585cb7a9aeaacc3b1fba6e883` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed6.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed6.json) | other | 508114 | `b211105d670f6160348849bc891744c66116007a187d56fb2b683a4aedb7b4b4` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed7.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed7.json) | other | 507226 | `af132f44bf30821c6edcee8aa724dffd5e2a115a42eb99be3a17c124938cbb99` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed8.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed8.json) | other | 495031 | `ed6716561de4eb0073c5766735868d778d64419797626dae4a2a41f0b4c4d2a4` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed9.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_cell_seed9.json) | other | 484104 | `f4b55ffc42441fbaa8df0d78fd04e6977065333b2968d048bfa8eed80974a771` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed1.json) | other | 502262 | `c428edba7582f5e70d77e7e03622a0db65f766dcb24073e4b74146d8f20c41c5` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed10.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed10.json) | other | 514782 | `12a9cb78e58d80e0decc40ce9d01a51efc35196e2c10a0000ffc52e3feab1252` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed2.json) | other | 506380 | `40817d667f2c773a805d15e046eaf969eb63d3774ce03ce2a4c4a8c0f0e2a529` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed3.json) | other | 501508 | `27c661d39135ad814779f23cba1eb2b5afd33def21c20c8752b7ec2f0314924a` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed4.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed4.json) | other | 518691 | `591b66d07d5a1c6714baeb2ec4b9b7880eaa9aa59b22413c860d6f7026785075` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed5.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed5.json) | other | 518353 | `e7ef0f3291c374fe861f33824dd4a2197117b36292fe2f41de9d78a32f7d73f6` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed6.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed6.json) | other | 510447 | `f856b4567a895b05d5586014040ab4930208d39933393d4a4436ba5eaef64293` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed7.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed7.json) | other | 506483 | `5618ecd2236d60b81bd924fa38acdb1a374c99583af34bef5cffb9771e2cf379` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed8.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed8.json) | other | 496504 | `873836381dab29a8f8a924d86f235765db3c3a9e695ec6b9f70ba310a11e40d3` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed9.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_colony_seed9.json) | other | 502246 | `371be5794c168554ac79c7a3acb2a01934262b10f5003ac367b60b43f39de900` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_pilot_cell_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_pilot_cell_seed1.json) | other | 504706 | `698b91606d1e542bc4bb8b7550da5d5c431b3a9315f0c1f04e6bda8cd3b273df` |
| [`morphogenesis/experiments/E09_pond/w2bud3/w2bud3_pilot_cell_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud3/w2bud3_pilot_cell_seed2.json) | other | 497888 | `f54a5800fb61715ad90fde6cb8d739ac1dbd1f4b3e05bf33bd1ec54104a4bafe` |
| [`morphogenesis/experiments/E09_pond/w2bud3_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud3_matrix.json) | other | 35616 | `ddbb2e67b6aa7f6a2a3de479462f95a6174b8e60eb76d3105dd451091f6b2554` |
| [`morphogenesis/experiments/E09_pond/w2bud4/w2bud4_cell_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud4/w2bud4_cell_seed1.json) | other | 518991 | `a06a997b95b93ad74f9e66a2c3b3d31f045c59b1a105548a6b4c06b29c2de0cd` |
| [`morphogenesis/experiments/E09_pond/w2bud4/w2bud4_cell_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud4/w2bud4_cell_seed2.json) | other | 512052 | `646041b01bca5f9baf59fcaa73649fe184fceeb53a60d85475abe9db6f55f08d` |
| [`morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed1.json) | other | 533814 | `e64d09322f9a057578a862277133fe849dd4f6a0cbcd40e57e2c926e1960956c` |
| [`morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed10.json`](../morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed10.json) | other | 531829 | `18d0bc6da474d7bc7228e6b885f5d5a0c55f2d4519675651c707343d780dd427` |
| [`morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed2.json) | other | 527128 | `550eed85942a1d198542df6cff1303c7c2b40832f490e1268a0fe3cd118461c9` |
| [`morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed3.json) | other | 529973 | `67d95c02f7e02b85a25ad1dd6e8548c9c9e737e649d8f4619f31917376a15c74` |
| [`morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed4.json`](../morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed4.json) | other | 534472 | `7130ac74df1ca09f92fdd51ae28ccda3b4c0f5bdef9b378f7f00a8f0477cf017` |
| [`morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed5.json`](../morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed5.json) | other | 556172 | `7b3a2d08147fa6371b524221ffd89331cb31f88913176a7fb0b3d39a6384bfa9` |
| [`morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed6.json`](../morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed6.json) | other | 537831 | `5dea56b48b6e05501b4b38eeb700ccf36bc87ac285923ade4491a5e3cead67d7` |
| [`morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed7.json`](../morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed7.json) | other | 537974 | `b3d399228c1a4eb68648ba49797ca4bb0f42f50c3ddd28a33f7c55f9b46d0a45` |
| [`morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed8.json`](../morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed8.json) | other | 524864 | `f1068598a18e912e7ad18e917880a617f81edb7fabf682d8bc3ceaf7b3aa0df9` |
| [`morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed9.json`](../morphogenesis/experiments/E09_pond/w2bud4s/w2bud4s_cell_seed9.json) | other | 511446 | `2745a3cb56b78af03a5a05ad288d53a50501250cf6478b88d8a65253252251fb` |
| [`morphogenesis/experiments/E09_pond/w2bud4s_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud4s_matrix.json) | other | 20241 | `fb938a2fc3ecdd108766ae34f9f1dada396c1f4bd79c60eaa76fdae5cc5bf073` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed171.json) | other | 443083 | `11496a31659882ed2653cbafe5aecd192600f8a5a83807634714718e4cd71fc3` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed172.json) | other | 485535 | `49fb9768f343c4d308aac82b495b273e4bfd91365255be93bb5694874972c7f0` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed173.json) | other | 475350 | `4e9f16ceb23b53a66226dd8a2e9e2a9b562295c838022898791b8eb6dc56ddee` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed174.json) | other | 449045 | `59f5fa315bcdc0809db6ff2a0ae09a42861fa2ca698b888aa10a26975e0dca61` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed175.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed175.json) | other | 500396 | `8dc5699abb02b7dade5515929e845c5aa76c57f8b2f462d8183a3218438b27ea` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed176.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed176.json) | other | 494857 | `b95c089e2728bdc62cb0bb50cf9f227c284c90b94469f8de0414692bb76512d5` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed177.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed177.json) | other | 498727 | `b869f586d5ea1285b97f6d176207826c705038e2935f81a099eccc30d5236628` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed178.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed178.json) | other | 453455 | `55911535c62889169d243ef9fbca784db2cde2d666abba305cf3179a83a5f79b` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed179.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed179.json) | other | 475288 | `d0e19611b601ac0f9c5cf656dd5beeef313da99e55ea12b56d1178f1e7a53665` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed180.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed180.json) | other | 454903 | `31fd3b93e6360877a0213d0513e387d4c6643f371b19269ad2faa6a7fd6a590c` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed181.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed181.json) | other | 467932 | `c2cd0459deb736b34c7c51c0a881fc0a3b171c775a2df182ef5bb92d2b6dcfc6` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed182.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed182.json) | other | 462688 | `095c37392975c686e16a482688091af18d25cdc965e39ad8378a2bba2404f7bb` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed183.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed183.json) | other | 486818 | `41e4ad3beef418713ffc252c33b2b7dd9fa0c0d229c8cc549676d4eb4de9abc7` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed184.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed184.json) | other | 513122 | `e0b8385f708e90b3942827a0d8bb17c01bf94add77dbfcba0050d5e7a21eaf8d` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed185.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed185.json) | other | 492602 | `9e95554a73199445fa97ba5115303614e857695b0eff70e6773af1b8a8167d7f` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed186.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed186.json) | other | 474082 | `e61a7866ff076a6332112dde974d19ca8b8e33d5542c7b7777cafad36ef4d513` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed187.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed187.json) | other | 506765 | `293a5594e8019f48554d3764590695a5a0cb1f99918ab2d1ac43ae34d6d709bc` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed188.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed188.json) | other | 495844 | `c05d43829c7864d2a631ae49639516bc8cfe40ddd4aa85bbb659ede62c521bcd` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed189.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed189.json) | other | 490562 | `5404c632925f94533922d1d08907375ded406b3ce2c744d7a3be648a3739871b` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed190.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp05kw_seed190.json) | other | 486650 | `d79c04546a147e239a6e241d6275bb44d5b7729380e08af52158e7ce7ab07bd4` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed171.json) | other | 700039 | `403a653fa457466cbcfb4b413b27056c0ac6f9fa8baa6967486109a7f0776f24` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed172.json) | other | 702881 | `4e25fa7ac35f14e2e1bc30a585b896e0cc82776450fc0f4a5ecc75f8c9a12c20` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed173.json) | other | 716126 | `fd556261022d8aeb977075091dd50202cbd78e7e70ff61d9aeb43578641a8faa` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed174.json) | other | 683271 | `badcc6e8e82db0a24820242da7342a723407eda94b0a7db064fa45f7a3a3b969` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed175.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed175.json) | other | 691257 | `80ded7f360c8ee3a445543b7ec79047d765bc332bbbf262d20a7d4b3492d0220` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed176.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed176.json) | other | 710454 | `78e0e40c619ead7e1efe2b236cb9648efaa3100ecfc3d31213ed22928e8d6cc2` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed177.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed177.json) | other | 686444 | `3b6f6fe49fcab443595949ca3d80e0f9b3dae506ecc22c59fe529139261ca236` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed178.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed178.json) | other | 709785 | `a177d5651828880e79e7b8c808f91dc79d7d3b973f8e08e018807aabf2b35546` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed179.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed179.json) | other | 696489 | `976e52ac04e8546beb44c0f866ce24fbcdc0ddde06b29f13964ae7927008e1e2` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed180.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed180.json) | other | 694956 | `62e32736db68fa96d8edd95842e5e7930b94c4b66f4ea280e8a11e53c3ecf9c0` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed181.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed181.json) | other | 722002 | `a69c1b17738323e22e9496bc869c1f40b7e657e1651a62843d4af33e8e55547a` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed182.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed182.json) | other | 694513 | `ef25d0f3dd9f3457b9daaec53ed35e1fc036ace82d8a35c323e9717853cdc94f` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed183.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed183.json) | other | 733258 | `2ccec3777db3b091b8cf865c2a566fbab69fd438177b26247b1328455403f635` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed184.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed184.json) | other | 697635 | `ef72ab0f8bb7073b21a5648cfea518e8091c0a3421b41de9ef23e37bef15e520` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed185.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed185.json) | other | 697494 | `3ceeb8c3fe5f75162a8b074e68d6c1e77b5694b6eb5a68ac4bdbe0b533674eee` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed186.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed186.json) | other | 684060 | `b73a338c7a924dd203ab5547b4b25f58f312143a436c3d5c65a055c87cbf43eb` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed187.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed187.json) | other | 677842 | `09255427cf72a101f4d3e1030a4094a7381929384b33e06ba6eaba6257fee18e` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed188.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed188.json) | other | 699530 | `76ac840fda382a04977d7644c82f8f6f14e5a821ba2d259824410af89612770b` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed189.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed189.json) | other | 674597 | `b23f8f20d2f0ab37c0fe05503552e5f9a92457595b0135fbd54592b9e56ac43f` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed190.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity/w2bud_add_cellp10kw_seed190.json) | other | 719413 | `16faf51b880b2b3fc6f1b9f7d2f178db6caf6ec0777e7cf2205de07d3a1f1f0c` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity_interaction.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity_interaction.json) | other | 1999 | `a374142aa290fb555ec74a268357e37a6c87abea016315b8471f1acd3a0c73af` |
| [`morphogenesis/experiments/E09_pond/w2bud_additivity_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity_matrix.json) | other | 66951 | `4ad7f4a40235502492c555e20b9cf81d0656d48c7f4978b75266892c73346745` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed171.json) | other | 423750 | `74552c8677ff47f3ff2d8ca2ebf426875949745539a22df76bb423b9d6131a04` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed172.json) | other | 441151 | `44d5f7f7b28cf8bb2b82c419261cb6281d5ec5d1ece45acd7b2e19913c545de6` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed173.json) | other | 454203 | `0e0a27a2bd3afe306423d46c36251c167b77e0e712ff307170fda954ac12b9b6` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed174.json) | other | 399255 | `9107322b2d18783d80b6adb8afc72723f75213db0e645f126790228eb0f2a982` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed175.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed175.json) | other | 456044 | `3d5a8efc4a7155aa93421879b25eff40d0ac620efcbde7315d322027165dcfa4` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed176.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed176.json) | other | 434733 | `46e51f8efdc457baf218e65301ed29a08960bbbacf20b2452e794577d10be6b9` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed177.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed177.json) | other | 457907 | `5b77136f49bc470c1bf342ff23253acf4ef71196507d498fccffd2d6f12d196e` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed178.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed178.json) | other | 420369 | `96bf790f2294337f5eda58a9ff805007aa55bc49a67d252d7cf4317e31150fa3` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed179.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed179.json) | other | 431617 | `38cd1be2a498dcd415a2fd1ed41958d5c56da371f9ee1337129cf630243d3468` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed180.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed180.json) | other | 412208 | `bdde59e88dbd6cb51dc08f81316945764d91528508dbd86636f4693a04bd3e68` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed181.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed181.json) | other | 430969 | `9cfe0716171560a9d236f0228a6c2ecf51e59b130bd8a660b93948dfd6423b80` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed182.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed182.json) | other | 459374 | `d503f33b150045d861242992b6f6b26724ff11d950d58c6cbccb9884208ba2db` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed184.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed184.json) | other | 447859 | `8d1146919b837f409bb3c40ea10ca817cf312de5722553852fc279a8987ce7c3` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed185.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed185.json) | other | 445375 | `9ad1ba91bc45ebceb09cc6f056e503ba8f5fe4c68e3ba3ef57872e7a1b4d0535` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed186.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed186.json) | other | 440346 | `f6f3a1d98db7fe5c1830ac9f05a3e15ad56ffce97e818d22f6726a3c86cda237` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed187.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed187.json) | other | 450728 | `b8de4bedb528563d093451f01ff29ad5c452f760d199652cd7fe88f692541952` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed188.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed188.json) | other | 441436 | `1bf06218fa6573485ab0d1f2c9617c0741912c5df76df48e3a7410d5062903e3` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed189.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed189.json) | other | 424091 | `4b16c6df63e6873d4301ca2031bcdb68bd517d24fa1ae217310a59fe75a14876` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed190.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp05_seed190.json) | other | 445413 | `458db6bf67f2ce5007e22ffc08b3258e251714c41eed845772963560107361bc` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed171.json) | other | 516830 | `f01da140d778eb1851b1e768a0c78887a71ea99b1c5486d2b2a67056e21d5a80` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed172.json) | other | 528479 | `f479e0482b4c8abce98f49cc6d84cd7cc77b8cc7ab2e6ff699f821e7148fcfe7` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed173.json) | other | 512159 | `345885d9bff1e0d2092f613871dc0c1ae4ef4ac6eed9f303794ed03f6a670830` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed174.json) | other | 534279 | `bc165469254ccbedd73b28dcab38b0fbcd2d21285d427d31d04e1f51088822f7` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed175.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed175.json) | other | 522753 | `e3d92e4173331128fac51d3a0056a6c14558cbc6cfed1e19919a64a05bbe04ad` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed176.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed176.json) | other | 534430 | `6e234c0d3a733f75e2581204b6947e1c9812cba069b92e29e9e16c00dbde9ce5` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed177.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed177.json) | other | 505208 | `a41f9516dfb1825075850d4e7c1437d87ddf3af614389f03eda24413c3c89ebe` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed178.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed178.json) | other | 505232 | `b21d90af3f10dded2d4deac9fc5586fe08277040d8c940fb2f122d23809ba93c` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed179.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed179.json) | other | 517179 | `5bc141b6c60c40d795a1457773ebeff53bba264231c0d97781ee41e7ab2a0bb8` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed180.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed180.json) | other | 521715 | `742cf6ca6f46d2dd2b5d605f25b457edcd624df2c5c9fe9a0a51678f88e38758` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed181.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed181.json) | other | 504243 | `b43a1f7d32fa960ca22a74f1a9cd4efd7804c459b2cd5ae8b7c84339aa02d6db` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed182.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed182.json) | other | 490030 | `6b33bc5e6fcd5565e664d0cfb7ade018a6d407a4037ee03db9a9a5fff07c2f55` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed183.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed183.json) | other | 525416 | `0682d7a8bf6c206581310137bbf756f6d466b9ad79bc85cd3440d06c8ad9c321` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed184.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed184.json) | other | 520762 | `21e0149f609b1b1044b9aa42af2036cd670eb35c0ee30cad0a368080f7b6c236` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed185.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed185.json) | other | 502552 | `7c447173ec5b1dfe417cdab459948273fc4b361833068452238eaa7eab954d1f` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed186.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed186.json) | other | 523132 | `5991e1f4e279b12d9049a709786edfed071e1ba916d70e114af53737caa030d2` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed187.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed187.json) | other | 538179 | `e6d7315934b67043c75eb643768bc90deea42b0624006f73897b66c8f3a26668` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed188.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed188.json) | other | 509055 | `fe2492cf72506ebf12da1d32479903a980d282a4f565f23ae248632e048e467c` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed189.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed189.json) | other | 509868 | `cc4abca2b1f9666a52c5cb76e24ee1b984e2e54d321d4a0062dd64705e2437d8` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed190.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp07_seed190.json) | other | 521198 | `699545d49af3d47778988b752f1030dece48b80547b0a8744e72a56d801253be` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed171.json) | other | 619896 | `551ed990c1edd76cd85e7a1937aec3736dc21801f20c70bff3ca4218dca232ca` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed172.json) | other | 588788 | `f864e96b44dd1bea38fbb6df1f0a7cbc885b04309a3054435345478259168fbc` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed173.json) | other | 606216 | `8ca700335fcf07354fa2d0839af51ac46caf3d7222a065e7e9ab6a3a0b102909` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed174.json) | other | 608963 | `54bb869063fb4f0c8d8d2a7b76b41964e6c0d374b1af0b9d5c91855277852737` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed175.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed175.json) | other | 599923 | `c6122eba3604e54234f25eb44ff5a7a6030796c338d22079eb5be53db241fc1a` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed176.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed176.json) | other | 604138 | `b99061427f205078439a5ff6c7e165dec75941cbcb9e718968799350e33fb6bc` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed177.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed177.json) | other | 606724 | `bfc6f6259d85a5aa611a8e568ffb55f4d9b3d5437e7f04408e6f09c771b8dec3` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed178.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed178.json) | other | 585695 | `8508f5fc423258d48fb1b730bbf4f92c6dcaec91261b849b409a346767f40d17` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed179.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed179.json) | other | 599347 | `4a1a799a069150aff11c860c819f9992c53eebc952e75a6c559107d61452a2a1` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed180.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed180.json) | other | 604765 | `4048443b6c182840b8f749489c34e4f33310a2f1d22dc3f61b104f7ffd2bff73` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed181.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed181.json) | other | 618839 | `de2c1d028acbb66c25fac7926e88fc9777c7c1ae62553aab71911a995b90af47` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed182.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed182.json) | other | 614064 | `c29bb3b44869f76c90e0361a5cb6d7781d57dcc3826234ea7299180b1c3474c4` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed183.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed183.json) | other | 621372 | `2834808add3414b2a3b93ffa0d4609ccc316706ed1c39160340534960f3fac6b` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed184.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed184.json) | other | 604687 | `a4b3fe2b39577950ca61b227fa30c7d96a292452166d60bfe1ca6b05f64565f7` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed185.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed185.json) | other | 601235 | `2c0f23362f1725063bdfa9459c98ebec7d7c2474379841d8a847d1af61a21da5` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed186.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed186.json) | other | 610694 | `61f50e72558e5b9d96ad566888113eb41d653f37ec9f39fc2ed1c503b10c3d03` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed187.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed187.json) | other | 569676 | `36a6854775359afb5665a2e0cb83ed2078ffe2a7f0e563f6e2f96eaa5c297c34` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed188.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed188.json) | other | 592866 | `5ef536d14e69caad1c26587c7eea8fc9048c6230f24de61e5ba8a38872553613` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed189.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed189.json) | other | 589946 | `c3cad85a3b83e1f4e433d4821dbb445846eb8dde1c91a27748396b43602b969e` |
| [`morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed190.json`](../morphogenesis/experiments/E09_pond/w2bud_async/w2bud_async_cellp10_seed190.json) | other | 611466 | `c1fd61bd1a1b4e504243db7ba2a52c2b9e103b02aa31bde353a956d94c55e9fc` |
| [`morphogenesis/experiments/E09_pond/w2bud_async_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_async_matrix.json) | other | 97549 | `6ecb384ef6c327dec6b1b1f478349404679d87c49ee171e664271d0341052870` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00050.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00050.json) | other | 8366 | `b50abc7854ce31f86dc79119937e7e576db9b9b9cab8c4b7a4fc0760e5cf9596` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00100.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00100.json) | other | 8369 | `c6f58a76f690ce6a98cf9ca95c45b77695e36176b38c4f3bb4eacb460449c187` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00150.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00150.json) | other | 8401 | `25afc1eaa3df7d012665a640b7c480614f037be5e09ade561e99461732299f71` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00200.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00200.json) | other | 8504 | `7268d61bac64f014b0bfaa1b0bb8bf7a6a718d3187f1d807b91537c54cb47d9e` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00250.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00250.json) | other | 9576 | `7daa529feab19893cd8a31855af67f3ef6db2b3b88e2d959da7689082ad87f21` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00300.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00300.json) | other | 10281 | `aca08aabd47bbf992e1cc1700b2582d238ddf784f151bd2d4c342d5097d5ea27` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00350.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00350.json) | other | 10912 | `ac8e9156d3a070488185d5ff50527a8a4214fe379d0c4fd34842fa2092292d8e` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00400.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00400.json) | other | 10980 | `9f37fccba3bc17f3a343d0101acbc61d3b90f8d65c64f1edf51fdb2fe955a8b8` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00450.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00450.json) | other | 10977 | `3e5fd09a00e5b40360f0d5d99dba10f95dd31d4ca9027fd225b44f741ba10ef0` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00500.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00500.json) | other | 11010 | `ffab3dbdd50f1dd39f3bf10b4af76ce9a16172e30e2939cbd2e169a0b8c3e0e2` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00550.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00550.json) | other | 10959 | `0c87890b050ea2f530e1ef50a66f47dd0770033248a0920735eb4664c35c1ada` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00600.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed171/fields_00600.json) | other | 10943 | `3a5156d7fcba548c2210cdd3bd4d9e33d7d860283d5aba117174bcf0e77eafd4` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00050.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00050.json) | other | 8366 | `a14734e0856ef5dcc0e919b31cab82e5f101e451b70412f0b2def9f86b9494b2` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00100.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00100.json) | other | 8371 | `c44456d7a3662a09abd9a8576eb121fe001351e0253d7ac28b9ba63f57fac386` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00150.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00150.json) | other | 8382 | `6fa63d0ad11bb9fa85468e28a27620dae9b1e03168f18a8d0d16deb02811e147` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00200.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00200.json) | other | 8411 | `a5bf8e94914bd828d3c565b99db3380d56f06b44c789a4a75bad3996c1e1d051` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00250.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00250.json) | other | 9218 | `c9ae6de94fceddb5d642ae08859e66602c9d4bc62128a2db9c5259f2d3313c79` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00300.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00300.json) | other | 10032 | `f45f541fc681c82a816af9d11059e40ab872fab088eecd3e912d9cb456bc94ee` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00350.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00350.json) | other | 10707 | `75e3914e6e0d6628f240112e87b89ead9415a01ad64f54386afc157c4e218cfb` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00400.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00400.json) | other | 10957 | `6341d466ad05e27063ef901b9d9df305a1b06a79523be01c79dcfa566dd42d51` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00450.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00450.json) | other | 11057 | `fc5b0e7a3489492b8c37cac4f9b88e71f3145627369ed60c23693a546d2fef78` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00500.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00500.json) | other | 10982 | `980985729ec2c30171bb25bb264a11a19373b85a82f33d6a10efcf1e5cf76c49` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00550.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00550.json) | other | 10985 | `39dfb45673a7303d8167252b52ac044e6f4f301227e1033173f5a903a1dbec44` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00600.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed172/fields_00600.json) | other | 11045 | `21f71386af01f09f9cf3c89a49168330d20be84722475f69a39682bf8b352efc` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00050.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00050.json) | other | 8367 | `30dacb4f8482f544660f082c5886e19c2b89777a4feb12db976a65a8f2ac2185` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00100.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00100.json) | other | 8372 | `614a77ef348ecef347c6f8ad84248b6ff1da9aae3f361e57fab32a0144e7cb7f` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00150.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00150.json) | other | 8392 | `76e52f3e88958e69049568a9aa96f8afcaa86559277d01fc95c6c4b57a348310` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00200.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00200.json) | other | 8432 | `d01d39f31f1068e93c468a5b15a0f413a4e50d4d2a34bd0b66d1157321f4aefb` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00250.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00250.json) | other | 8785 | `51f79be91f28497dc9c7b1fdc1b39ca0f6aa29b1fe53bac6e4b8c0a48aeb98e4` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00300.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00300.json) | other | 9696 | `ea14cf501bd34eba175858e686600d823e8bb622e2ef033e19ddfa8243814200` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00350.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00350.json) | other | 10325 | `552cdf72c244f9161447bd2bdbb0500a9e4c8379f5dce6deb2c1602ec5754ca9` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00400.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00400.json) | other | 10931 | `201f650a463306e6581570d938c14232408317f16253b1cfdfce2348c07a20c8` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00450.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00450.json) | other | 11005 | `1b54c23bef8860a2717e0c076d443782bbff850cc328227c2dc7dab17dccf321` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00500.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00500.json) | other | 11007 | `0012e74c7d18768db69ef2b8c6e7012e2139b99e2d3de6c925e88b44a8910ed9` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00550.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00550.json) | other | 10988 | `5694da820d128c75222f1b0dddd9a80599ec286c80546600e48e661f2fe96a85` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00600.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_normal_seed173/fields_00600.json) | other | 10937 | `b3934ccdcc9570a37d2a9e31956b66325d11ace3d81144380b2c52dd929d0de5` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00050.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00050.json) | other | 8366 | `b50abc7854ce31f86dc79119937e7e576db9b9b9cab8c4b7a4fc0760e5cf9596` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00100.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00100.json) | other | 8366 | `6860b572be36a04d3525267d36677ee2cdf51f912d7038b4d0411db137493ae7` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00150.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00150.json) | other | 8369 | `298e564323385067aa986b4ab7788c9f482f7b488836d30e8402eaa7fcbccace` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00200.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00200.json) | other | 8369 | `0f34ec57729c66399a54b3afc7d34a7b3d458236a7a11ba67b32d6bd062b1461` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00250.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00250.json) | other | 8369 | `94ca9baa6f73c86fec51f1be7cdd283f3061ed8f316d80865fac2f94390e7190` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00300.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00300.json) | other | 8367 | `275041bbeda2dd25d0fb912a7b7a81467da8be93585680006ace89d2fd2210b2` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00350.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00350.json) | other | 8368 | `5dbc048449e3c70398623221f30e0c8cd62d85703f69110846892f0864975bb1` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00400.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00400.json) | other | 8369 | `12b767a95f60e870862b997dbd05d4d7d0c3981e917e6613044dfe3f5fd2ad29` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00450.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00450.json) | other | 8369 | `2fc8d62f0c907fb66af926e601aeab52dd3ba9c39d1fbd2628719adca60c8778` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00500.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00500.json) | other | 8367 | `5e2adbeb227bb130941d3e839f9c9cc3d57ae98e04231cf7556d4d2002935e52` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00550.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00550.json) | other | 8369 | `5817811c81e534405cbae73dd6c07e4c94ffb8463f8831604e4d8656b69c9c6b` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00600.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/dumps/w2bud_e1_null_seed171/fields_00600.json) | other | 8369 | `ee3055fa81d00b30d473366027ba6391ed7934a13a24f5d14db1c42dd63cebb9` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/w2bud_e1_individuation.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/w2bud_e1_individuation.json) | other | 5513 | `30a7acb49515a6107eb4fd55c72915a845bc591e9a20a86fa0d6eb41d5c3f77c` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/w2bud_e1_normal_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/w2bud_e1_normal_seed171.json) | other | 530714 | `02ee5680b08b0a2d970b269360eef3eeb996ab7b852a028712c93950accf2411` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/w2bud_e1_normal_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/w2bud_e1_normal_seed172.json) | other | 498793 | `bf5170843428c79c819c3110f87cd8d80b0c58769bf54d763f13141138929928` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/w2bud_e1_normal_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/w2bud_e1_normal_seed173.json) | other | 486200 | `e107587b2933eb28b91d863ea5be7190f0ee1ad6c515c90876db9db487d68dc9` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1/w2bud_e1_null_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e1/w2bud_e1_null_seed171.json) | other | 333475 | `bd2238da7c86d5ffbe336bcad13d4222469bb7910b11885add07cf1b61957f0c` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_e1_matrix.json) | other | 8139 | `b9e53fc0c913c7057d2399327c5665b17511bea981bb27f6533afda2e5040846` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00050.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00050.json) | other | 18759 | `123c429ba911fbb4cd335749e3966ebf8ed370a7147457ebe7b637bd07e64c35` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00100.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00100.json) | other | 18767 | `c2372478a4d7500526064ea44504408f60b3447aa065759ff5a35fec0d9f54d9` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00150.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00150.json) | other | 18805 | `b04196f3a0af714cf5b2f5944f2f25a8613ec27c62f3488e1eb4db6aba6f3990` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00200.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00200.json) | other | 18930 | `7283b326171a6f0904aacd9cbb12aa746ab18542a1a5675a79864500ef81e88c` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00250.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00250.json) | other | 20317 | `28582cc108433a1e87da281817e23405eadde015a6c167a29cafe86124cf64c8` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00300.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00300.json) | other | 21242 | `7afe5a2cf077985c61a9d7ec832f8fe799835e588596551be5084aedaf033075` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00350.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00350.json) | other | 22155 | `5aa49fd4b1bf693bb97b640ed1700e566d5cd8fa125062955c5ea8f66bbd9bcb` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00400.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00400.json) | other | 22229 | `ce3555ec0c78261cb33a593a5ff1c581c92b2bd52bd383fc97b80ed568c62b9d` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00450.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00450.json) | other | 22130 | `b262c161fa36db186916f3c0636f8b1b8faa8c6c789e7e2a12522843b1b66b9a` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00500.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00500.json) | other | 22054 | `b024c047081076cc7960737f209716b397f21bfd8aaef766835396a3cb4d6da2` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00550.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00550.json) | other | 21918 | `a0560973137ee5c9d295b389d0f2c5cd6d6c6577fccd549fa18a1f7535e7e834` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00600.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed171/fields_00600.json) | other | 21912 | `d1ace017876ad2e72fc0e1712432e155dacea3702d433b32b571b25b0836e7ff` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00050.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00050.json) | other | 18759 | `a71e9766a54c09516489e75ff9fdb41d9471ab92e90362d694c05d671be07d4d` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00100.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00100.json) | other | 18769 | `343dd5a0136e189161ff125b805299488c26cc460d3708afa34c7d2db27f8a2e` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00150.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00150.json) | other | 18782 | `c774e25358db959c3efefb3b85caa8f14542a3e17caabf729eae5888161b0919` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00200.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00200.json) | other | 18821 | `d9ba9f5591363927ed5b373aff402d23ca34ea818f88e929a54e4ddca11ec647` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00250.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00250.json) | other | 19833 | `0f2b27bdc81ad411cd22ed97a49db61ea23aa7e9629f0598bd2fa0fe95881367` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00300.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00300.json) | other | 20915 | `1c8641618dc13bfdfe3d03cada3f023be051864f1c42b44922a8dff0f638372b` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00350.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00350.json) | other | 21915 | `b726e811dad46811b89473489c24155c44edffc0ac52541d152c103e40dcc41b` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00400.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00400.json) | other | 22187 | `04b13635cefe98aba6ed2f287acda630d9bc85b6067747ee36a82612f285aac3` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00450.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00450.json) | other | 22237 | `4075dc5db92cabbb41427677b90ba3ddb7032e23712d097f1751f2c47ddb971b` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00500.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00500.json) | other | 22098 | `4d081fe35507e632c0f324da33cef465dc475d0e5582776c8969a85cd927fd92` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00550.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00550.json) | other | 22054 | `1b75057b2baa4858fc2914e2111e1345f215107af09629710b57c82dc4eaaa13` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00600.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed172/fields_00600.json) | other | 22161 | `e9f20f71b94981eeb82533b8f17f9b06d81d99a39bd6e6013b8051c8825c444c` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00050.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00050.json) | other | 18760 | `d35f0a9d4e4b9a690c63123f85c11e7352d79025d1fdd8534b2ebc05d190b502` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00100.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00100.json) | other | 18770 | `929cc885aac918d0b6f8a45166294486bf98ad79de5bca99768b2f33692792b2` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00150.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00150.json) | other | 18796 | `0ce19534bac26055e701655c274156c75b5b467ae6ab10fc69ee67439381e32c` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00200.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00200.json) | other | 18845 | `baa2e6c07741793593376b3cbe84003524f9fc8cd0123bd0abdff9af19684e42` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00250.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00250.json) | other | 19265 | `2b07da8a7ccd9c67da9b6401f91f5e88eb2f9a45182c8a98ed58f1b9d2908e6a` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00300.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00300.json) | other | 20488 | `89941d4e3121b30b0240b2e07f5387fecfd47147106c15a425fd461d326d20e0` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00350.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00350.json) | other | 21343 | `a46321d93a84b82c68a176003de18a68bca63689afeb923e7baf9b5b2823cf7b` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00400.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00400.json) | other | 22148 | `4b712e60cf6d63df3d1802a94150c42a9505e4e7dc253cbe947f75c325384e27` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00450.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00450.json) | other | 22218 | `cff4080f6454d1a8eee1129093fd0aaab52400084836ecc88c6a1136f4a06c28` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00500.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00500.json) | other | 22140 | `419cd3337564ef205b2cc2c3a05c9fdb69a98e4c2f8f7dc607bcd766a94c3970` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00550.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00550.json) | other | 22034 | `84b3466fcb794c63b45af0b6eace5de615a3b8c6d8917aa86cf709170b8d2bd9` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00600.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/dumps/w2bud_e1b_normal_seed173/fields_00600.json) | other | 21982 | `42c8df39b7adb7c7f3fbd508502a0161803738024a01c27574d397ac9eaf9903` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/w2bud_e1b_normal_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/w2bud_e1b_normal_seed171.json) | other | 530715 | `45ac04b61d522d18fb77d590a7c8d50549f2afcc01cb8a34a384c02e3bd623e9` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/w2bud_e1b_normal_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/w2bud_e1b_normal_seed172.json) | other | 498793 | `ec6fc0dc22b8a044b710b54c40c825747d64ee015c1a6c1bce6f4752298882b1` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b/w2bud_e1b_normal_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b/w2bud_e1b_normal_seed173.json) | other | 486199 | `3c8a76aeb197e34209b9b520af1cacc8a27eca00feb4ba34ff48d188498b5613` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b_individuation.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b_individuation.json) | other | 2278 | `5dc55ee70bd2f9782583e06073cc6fd7bf349e903b2cb878c0ec82054fdf3e63` |
| [`morphogenesis/experiments/E09_pond/w2bud_e1b_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_e1b_matrix.json) | other | 6594 | `d24fecc2e3cedf2ce863939aeaf7c2f3f9487c90c1fd910c333932dce55f05cd` |
| [`morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_const_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_const_seed171.json) | other | 894670 | `3d09b3480a6de37f26647f22a8dff9f038192a8487e52e5984262334dc294735` |
| [`morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_const_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_const_seed172.json) | other | 838014 | `a521cecd0882a73422a843e5f4da55ac73f95e7d553c06330d007735d33c511e` |
| [`morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_const_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_const_seed173.json) | other | 837032 | `d78c3583850746da368791e7181438a342ca0f3a2102dafd455669b78e415a16` |
| [`morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_fast_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_fast_seed172.json) | other | 919888 | `fc4ccd8bf7e9104062b28fc465bdf1b2a113a020924c904453ac01aec96b462d` |
| [`morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_fast_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_fast_seed173.json) | other | 940321 | `5186ebd6fc6cd7c9d4d72349c44bd44d0a42241fe074f46bb84edc653593a53e` |
| [`morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_slow_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_slow_seed171.json) | other | 771748 | `887fc673e01651adb88cf911c9bc697aec29bed2891e524bf63ce08adc73a393` |
| [`morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_slow_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_slow_seed172.json) | other | 724975 | `042108f2323785ed9578feff60a9251d396fb5553d2f08846149023495c0662b` |
| [`morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_slow_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e3/w2bud_e3_slow_seed173.json) | other | 755650 | `744cd4b4bf8a9b90b35a2f957c23df7e0c8574ecf758d9b9f360441c3dcc5c8a` |
| [`morphogenesis/experiments/E09_pond/w2bud_e3_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_e3_matrix.json) | other | 14530 | `c13346842e60f5e246331207891bb36097146216908a1fbf6fd12955f3c238ca` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c000_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c000_seed171.json) | other | 530715 | `ee6e635a6e3c0af98ea5aaddb1257f28f661c9b4ddb6d4f936e2564adb9b6002` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c000_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c000_seed172.json) | other | 498793 | `9096776bfeb60c8c931c70107d49dbccd4818a7974bd86ea91a6c0bfe9b9ab82` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c000_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c000_seed173.json) | other | 486200 | `fc8d14b2ed063dde6815d50ea57bc181e6684b7cc2a32fef1c295223ed17b189` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c020_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c020_seed171.json) | other | 513079 | `4b8c7086885cb40d8df2e2b89c893248ba338a53e4e690c6a5a1aa29f4948309` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c020_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c020_seed172.json) | other | 513441 | `ed9742d0733881ce4d8248955aad613e02ebd8ebb430d5a8f22fa25a1025a6be` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c020_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c020_seed173.json) | other | 469500 | `400aaad7e58e4126f56b80256b54cd65f4b6bb3852d18baf6f385f5ec880cdd2` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c040_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c040_seed171.json) | other | 508972 | `734771e1b6f5ebed2d75c177d96dd079f3f12467d5a01a887f25ea59ef25359d` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c040_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c040_seed172.json) | other | 503633 | `efbabb673026c2764852e27504e0cdf242fe069e6901a3be5578ca884df9c02c` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c040_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c040_seed173.json) | other | 516424 | `3652b51c9cd0f8b9cd685ad61422ae0fa6dcc79f7dd485caa48d6d0903b6cf72` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c060_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c060_seed171.json) | other | 520814 | `6078248dcce78fadd657ae4b0f6ac911afe838e55306632ac489bcec08257dee` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c060_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c060_seed172.json) | other | 493766 | `a0ceaf4ebe8d1a4f24859e2702faef98586cadae3a8235a834799ab1e1640f7b` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c060_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c060_seed173.json) | other | 519298 | `b804b1164d0f72e42140babbd950c34e85ce42c5d8790906cf0df5da9c409c0c` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c080_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c080_seed171.json) | other | 489945 | `99ae324585eea8367bf57497520d9553cfd684d46369983d4e15dcdfdd4055df` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c080_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c080_seed172.json) | other | 509197 | `fb4600bf415be9a8648e39e27174f4d51862afc7e979c668787bba24faf6ffed` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c080_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e4/w2bud_e4_c080_seed173.json) | other | 455838 | `2ba9b186cb7f88745d955bc562759bc1d37c06d3052ee48984b524f866723b5b` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_e4_matrix.json) | other | 25579 | `43be11fa11d19d56d5213a1eff32f9109e078b57e22c4c5899c92c56c328d5e1` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p048_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p048_seed171.json) | other | 462784 | `b7bd0c876cd376a01d27474e52c16f7f770df20b2021b50b9edefcbb8747049d` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p048_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p048_seed172.json) | other | 432439 | `20ad5b8f0c22797c955f9de015abfac8d86115e7f099fce97530a89505e29504` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p048_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p048_seed173.json) | other | 464949 | `347c0165075eaa69fd64a712596a6b772fd67d806a2e21c71d6bbca8c4a8a6ab` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p053_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p053_seed171.json) | other | 439354 | `f1c23e498fa95f086d190c32b264d23c01ab954f1c01030e7ce06685bad24b37` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p053_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p053_seed172.json) | other | 469029 | `c8a8f357bd89a0557c1496742c2617033af3c58d0e8bc80330f60e780858ae4b` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p053_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_e4c/w2bud_e4c_p053_seed173.json) | other | 434835 | `b62aeb651a947ae6e053df8e66ec5138f86185c378c50005044a6cb98eefd69b` |
| [`morphogenesis/experiments/E09_pond/w2bud_e4c_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_e4c_matrix.json) | other | 11328 | `069dd3c8abfbed553df03a567ea34ae8e0bb71b53bc344ba3f6fcb6e7da5acce` |
| [`morphogenesis/experiments/E09_pond/w2bud_hb/dumps/w2bud_hb_live_seed171_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_hb/dumps/w2bud_hb_live_seed171_heard.json) | other | 12305 | `2358e8e2d55bdec236e3c73c75d1eab62331537506f8083273efa83da6638881` |
| [`morphogenesis/experiments/E09_pond/w2bud_hb/dumps/w2bud_hb_live_seed172_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_hb/dumps/w2bud_hb_live_seed172_heard.json) | other | 12277 | `6546027efb1a0631ce8e7cefc03369f89555cb878fc89c2ebad5b23938cc9610` |
| [`morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_const_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_const_seed171.json) | other | 891069 | `b34d77f7b85319638464452b2b980503304a1dd260be40d9915df71e60319fed` |
| [`morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_const_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_const_seed172.json) | other | 856479 | `aee9c3926c9e2ff2830c66a1cb3ac5d0838a110d16bd2b654934b3f51d9305b7` |
| [`morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_live_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_live_seed171.json) | other | 844684 | `9c55908517677010ba07222da799cfd7808c88a33df9eb640513a1beb6ae0e4e` |
| [`morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_live_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_live_seed172.json) | other | 818095 | `439a3058aff07209d5bca646fa147a24e25f3675f6ec9517253d2d8f38d7708c` |
| [`morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_replay_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_replay_seed171.json) | other | 851305 | `41e79ea473ea092910bd728331977c030d6b03ac0cf062b24d16cc55289acd76` |
| [`morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_replay_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_hb/prequel_async_read/w2bud_hb_replay_seed172.json) | other | 813801 | `ba1b72ad20a003e4902c1705a09c72b491445d153dc15864980cf707f5c3694a` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonboth_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonboth_seed171.json) | other | 2186160 | `74c6f79e1ede70a4f350beb0328175d32db7fb5a0e828c5df95863e683fc6623` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonboth_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonboth_seed172.json) | other | 2228054 | `7bf9ca29aa13e059fe2e9893e9e99ae5396b47ce7cd265473d7c54a7bed4927b` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonboth_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonboth_seed173.json) | other | 2189518 | `c1561ad5417a14bc64696c81cef2ab07c838e73535250d3d3d9a7647d8d7a1f9` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonboth_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonboth_seed174.json) | other | 2134748 | `7e39f31b5e17e3305d89f8c1ce8124d56e89c870c89a45920e107c906eba1f7c` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonboth_seed175.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonboth_seed175.json) | other | 2181189 | `0564fdea7d56da28a236544ef0e75b3a530d8a03b9a0f4fb2d69e2633742b222` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonc_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonc_seed171.json) | other | 2165588 | `3adefc4496d5d699d99b9655d823bed0d6356dc8016d3cb0612e4a0f4dc2e342` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonc_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonc_seed172.json) | other | 2153243 | `0f69da60eed987441723353db12c5a1429225c3278dfc52f0103b78f96771062` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonc_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonc_seed173.json) | other | 2112728 | `80fadb93d72f750cd828531e2f44bc8932be9fd6a6b60d57960e61c969580d86` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonc_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonc_seed174.json) | other | 2206831 | `be37542bb57554b5697a25f340e88a19029d73cc453075d886e3b436c935c62b` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonc_seed175.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonc_seed175.json) | other | 2120162 | `f7cd53988de8748799697f81403d5e841fafdff6435a52e2d2108f372e422cb0` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonp05_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonp05_seed171.json) | other | 1815774 | `a5ab8bd9182410c0ef0aeadaff3bc205c3bdf0ffa4414a4fd647b4541f7eac2b` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonp05_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonp05_seed172.json) | other | 1823722 | `e6c9f92b32cc0087f4749899f1cf70262b39b5c19bed2f0a6c81d9259b1d928b` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonp05_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonp05_seed173.json) | other | 1868771 | `091b5589d00e471f33fa5fa2b1a4ced59b9b6205294d969cde039b9373d974f1` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonp05_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonp05_seed174.json) | other | 1811893 | `bfda1da8b577a6e395d17ec4c14a873b9da4f362b9381b38d9d16f9c7b614fa3` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonp05_seed175.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon/w2bud_horizon_horizonp05_seed175.json) | other | 1791432 | `68fff4a1bdca9329719b82a385023fa9550478780a70a012610ff0a483bf6dfd` |
| [`morphogenesis/experiments/E09_pond/w2bud_horizon_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_horizon_matrix.json) | other | 27184 | `f1696bcae4deaf554b9684983cd068c7792a68a010067cb9762d60380cc6cd49` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2/prequel_two_heads/w2bud_k2_ctrl_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_k2/prequel_two_heads/w2bud_k2_ctrl_seed171.json) | other | 1181577 | `9495b49ef0e6bd78a809a603ae25504e0e6d7dcebd7dc584368575ed9ec06aa1` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2/prequel_two_heads/w2bud_k2_ctrl_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_k2/prequel_two_heads/w2bud_k2_ctrl_seed172.json) | other | 1116817 | `a82239f4a354acf885e10d1eb9615633ce10254d83f40f78552cc334d81ba059` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_async_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_async_seed171.json) | other | 905276 | `bbfa66ff61fe422b82d4aac8934c5e6c0a565da85991daa1cf63d2b8fe9b537a` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_async_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_async_seed172.json) | other | 922029 | `23de19c01d4abdf58c2f90cd4f0fc114783adf5e62161413fa64709b009112da` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_async_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_async_seed173.json) | other | 936274 | `9111a91131ddc5f0db72d94efcf3c536cf387252a0edf77325a15832aab64c4d` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_ctrl_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_ctrl_seed171.json) | other | 1181955 | `9780a367f34be1d766b3c17908a61a9d6409433f2ebb8e366c9dbdc5d3b0e967` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_ctrl_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_ctrl_seed172.json) | other | 1117193 | `4418dd500557e7e98befa23b2c788c9299779cbdd8acebee743ad6dbba0bc023` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_ctrl_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_k2/w2bud_k2_ctrl_seed173.json) | other | 1132016 | `e8907520d936f2b194eb99a4841c85d0e5507c26058e2a2486f8551ab0af4e52` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_k2_matrix.json) | other | 12131 | `77cf19522ae38899e76b651c0ac293094f3117ccb4fa1b752aa101b68807229d` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_async_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_async_seed171.json) | other | 1983247 | `622a10aa94e88c35b66db51c8ce919b91634a2164a7b7dafb1a1eb981f24f9a4` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_async_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_async_seed172.json) | other | 2001374 | `558910675e392719f0bf0e06d7833a68f936183ae3b14e6464e3f095d41b7a87` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_async_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_async_seed173.json) | other | 2045954 | `1ffc12265bd7d7b859a904e122564b909c25fe84fd30839a53d1fb39554c4650` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_async_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_async_seed174.json) | other | 1989408 | `9b6a78efa60b1efb8917b23931b844972db932d19e85824da51f2a52cc1327f6` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_ctrl_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_ctrl_seed171.json) | other | 2355934 | `41b54f5def982b8e4fe62338944a4d5e2eb8cb2efa412de349ba0ba73fc30292` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_ctrl_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_ctrl_seed172.json) | other | 2342467 | `87d4460243a8e4c17b70118641145db3b3c1f1fb15b4ee4aa06d41d9d49a7b8e` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_ctrl_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_ctrl_seed173.json) | other | 2294637 | `dc0cb89234980b95d875d54f18ba23dd4a77a67148929907cb585a5db4d9c5ce` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_ctrl_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_k2b/w2bud_k2b_ctrl_seed174.json) | other | 2386711 | `234d5c9781138ccecb5c9d986017546a16dbbff590e9c1eb5ba1ed09eeb36322` |
| [`morphogenesis/experiments/E09_pond/w2bud_k2b_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_k2b_matrix.json) | other | 15407 | `64a43abc0448a88ee0eaf5fa29696560cd01d282c84e1a59b62719d8be4a888b` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_const_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_const_seed171.json) | other | 454077 | `ee0007a2644bed8e31e2dd16e90e7e68703e830a167407c20a36d0fdc11c91b3` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_const_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_const_seed172.json) | other | 439932 | `ed6f8a41192c888cead4b519753149a71200c3076f9d0cc5c804c210d13dd454` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_const_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_const_seed173.json) | other | 411354 | `030d15afef0172ca4b21c1a6e70f73db5cdc7596a5284655ba9f40eab8679522` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_iaaft_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_iaaft_seed171.json) | other | 463484 | `d28c6a6c7ccdaf753e080a2fede70288e372a187518324d7898c6237c064580d` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_iaaft_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_iaaft_seed172.json) | other | 428074 | `f4565c73a48d8a2d0710b75e56733576058e3a3c372f1f00b9432bb55258729d` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_iaaft_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_iaaft_seed173.json) | other | 417213 | `9de45f43db3cb6a0caa98e876d16989b303f3f1785ca9f28d8c6db98dd74614c` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_real_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_real_seed171.json) | other | 445598 | `d34c44132dd3f16caf68e5f555845128e6c245d405e5aa4ad46f792803c23821` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_real_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_real_seed172.json) | other | 428461 | `9c92b3a7b0b7db05ccfba33ef5c49863e2f209a4b7d679e7cdd6f5060b75ba9a` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_real_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_real_seed173.json) | other | 432911 | `a527a17e2403156ba4f24e818d8047fd08228f4ba56df36fc3c79b04196c4d7c` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_shuffle_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_shuffle_seed171.json) | other | 466643 | `d148a4aea093a6f6b88d89414f54fc170684218c56903fb8fef404e38f941b5a` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_shuffle_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_shuffle_seed172.json) | other | 388316 | `7e47d0acc9922b80609eef127d215964702e2187014146524ce5758b2c3410a1` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_shuffle_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_k3/w2bud_k3_shuffle_seed173.json) | other | 417744 | `a0061642b1c3522c674f4030fb77c8b9f20b33eb81bff21f9207efa529c14a09` |
| [`morphogenesis/experiments/E09_pond/w2bud_k3_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_k3_matrix.json) | other | 22408 | `b92e1f1a7a0254be419fcd0d9d1219545b9c534cd5a2665beff6c2c16a1685ca` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed101.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed101.json) | other | 597391 | `e8b13b8dc9170fe06141a2fb7f07552afc88ef6c64173b1e9c12240809e3c2da` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed102.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed102.json) | other | 604137 | `dd5e423c7caa3c71064b0d6c55b44cbe422778ea44bbcf7c7cf5ddcfc72c5257` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed103.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed103.json) | other | 620747 | `b537d179fab21d747cb7e6b604dfc0794a9157dd7e4d867819c50f69d79de8ab` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed104.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed104.json) | other | 630646 | `ef471de2aa58251f3ebf376e385ab194e36c135c57699feb83813afff79dbad5` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed105.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed105.json) | other | 619762 | `61b9719eaead731b18e29d26ed72ec0d487003ee124f50b8e9e546379d8ebc64` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed106.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed106.json) | other | 603991 | `85874fb5ee8db206ccce696a59ab84f076575e33e12049d6232d69f4ae3e554a` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed107.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed107.json) | other | 619104 | `f021b5fd26bdc759dd01c0dc1ededc058650d339c4ed9fa11045785ea30f6c95` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed108.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed108.json) | other | 606875 | `b364a457b1adc3e0edd09b3b9ed65c0999684bef13abdede72e3fa8b7217611c` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed109.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed109.json) | other | 606255 | `f5e304061739a71fb0e8b481419203061aab2acc9616085bb3659128ce80f12d` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed110.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cell_seed110.json) | other | 592450 | `4746568b1fefb69531cb74f8b9775b3ddd5d92f2b4ae7ccf4e871b1ea4fb3081` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed101.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed101.json) | other | 636304 | `93dde3143e50ec1ed8d4ca85b15fb9ea1d0bd6d58df676e4b732c3933104f0b6` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed102.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed102.json) | other | 665818 | `7a32e5b5d388c39aebd1942daaf235daec1323183b68a33dfa4322e708b5e7e0` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed103.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed103.json) | other | 678595 | `252865bcfdc0af756a24199fb2addb8b5d433e9db9d8eee76dfd5d3c72574ad7` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed104.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed104.json) | other | 691717 | `8f0055bbfa288669a57c43e91c73621a0d5878dd89a8defcfb325e087e06dd1c` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed105.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed105.json) | other | 658089 | `f30ba7e2c96980da0f43d124b48b269e6fb87b1cce6f54d64e6f47f7fb641468` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed106.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed106.json) | other | 649871 | `cdd9b1660361415a0077298031480b7b0bd900b4f4b4ec1a3e870e868a72a288` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed107.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed107.json) | other | 664520 | `ac0665a575b446751ad5086ece6a2ca7dd7be0711c2017d9ae489311a46d3772` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed108.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed108.json) | other | 681219 | `f8e3de8de811e07ec41b34e87745512daa2f51cd9c2e7f9ff3afb285a78c0398` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed109.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed109.json) | other | 684700 | `a130be9503bf14896ed259befca246d91b1426115c7c8957adfeb13c58a66d81` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed110.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw02_seed110.json) | other | 654857 | `e5f40b23e80298faf4a47b4f4f6c6d8a3bda4dfe0079d23a758aa71b5a3fe0fd` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed101.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed101.json) | other | 668064 | `a0aaa88b5de3c0c3b19c938883f70a1266b6a2df47a0bb8fd5d29b6768663c97` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed102.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed102.json) | other | 696431 | `285a2298ca8ff6111185b303aa93da63c9bf613d578dac067023570769c65fcc` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed103.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed103.json) | other | 745375 | `b169d3768b341ad56b980c8479672bc4264180a3821766f534391be103aa3d54` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed104.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed104.json) | other | 734419 | `057da90030fa30a646bef82877c1157b2db4ac0cd1190608a62b4897526bf902` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed105.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed105.json) | other | 685982 | `70972670adf993a7b37100edbeaabd5beed08daaf628ae6e54af8d2297962428` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed106.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed106.json) | other | 701352 | `7ecd22e54ce1efb7c9d0430b2c74561be8a676907b382e4b97ad1b502c30c823` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed107.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed107.json) | other | 706135 | `f3dc4dafa364e7e0dcda5f3c37cbc65eac5baf1714d1e285d550429071080050` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed108.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed108.json) | other | 709458 | `a74fa31377da1bf43acfbf2850a6e517391adb5a05886fc2bcc45765c594122e` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed109.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed109.json) | other | 738056 | `d2c59dc42462956e0259435952b71db7a5d86857760ddc6542a78c0a04baa9cf` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed110.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner/w2bud_killwinner_cellkw05_seed110.json) | other | 676010 | `3ba2a866c118d6ef24d9353d46114c9c6875cf80044177f994a736d9ca70156f` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed111.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed111.json) | other | 695040 | `02745aa190c2366a8dad4c1fd26894c83d3e37dc05fd3547c9f66476505c0831` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed112.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed112.json) | other | 735147 | `6dfd68126b49911647df75c87984c04814660c4056bea10cedb293daabbe8a7b` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed113.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed113.json) | other | 669077 | `15f25e926f4a0255a79fafb341a5d8e1d1efc0d2e59563762cbb66ebd7630977` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed114.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed114.json) | other | 673283 | `e6602500852b6c1b8beb3835ec1d0af1831353e6b51c1158fb06efd4cbf768f7` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed115.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed115.json) | other | 647522 | `76e4bfe9ec3c52293827f89ecb4b52cc4b7424d80878166725bd080a09132f16` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed116.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed116.json) | other | 673617 | `d44f85434d936e97ab40d38b5a39ec6ff3b55ff50a487fd8c6e5819a7e0e69a6` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed117.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed117.json) | other | 694585 | `eca25d51a86e38bc97fb3fc16b6d27a7556f5f65d556e531f392db0c63f70b6e` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed118.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed118.json) | other | 720172 | `cdf9d7f6f4d229d49ef6aeb201bdba3bece8e992e6ae4738dbc7c5ee2a47cf0c` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed119.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed119.json) | other | 727111 | `b9fdcf270cbba9c70fc4941bbdc9478228e5752c63c4e41a7a8d8ccd2f59e02c` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed120.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed120.json) | other | 697696 | `b1414ad24b8d923c597a7f85f06ac166fb9726f0924978c2f77236425cc9763f` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed121.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed121.json) | other | 712056 | `4540401680c0327cd82c1eb5f074f161be275dffde29d4707a68363972f2d3b9` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed122.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed122.json) | other | 642007 | `7b082605bf2470e4bb2e4077e2a0e909870a643aac020150ddf9e270068f3da5` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed123.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed123.json) | other | 713152 | `4f24f311f7f891e88ca47b5d317bbda9e42630b8bf6a3c2f8ff05a3e8765ceed` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed124.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed124.json) | other | 709561 | `bd01684784a80592409b7aba3a3f6dbf9a58668f3cabcf2c221bdd6fd1416790` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed125.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed125.json) | other | 706739 | `cd3c20dba42f7c86a4820f8d2e54fa77946257ba2acc83803580092e3e9fe124` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed126.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed126.json) | other | 704908 | `5d87fd612ef231c0e051b356e138197e8b0bdbea04839434e96e652d2eb46d8d` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed127.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed127.json) | other | 702873 | `7c2c0523eb12ad1f9bd509b104e45d6cd43d66f2c62b9b682ea5358faf4aada7` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed128.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed128.json) | other | 733064 | `18a1a6ede3c23fcf1bcbb89d34420cb4427a4e66064af2079736d80530b94bc3` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed129.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed129.json) | other | 698027 | `c3d7101dd8da512924d6caeeac5b59a0ee1e986d08e13e60b120f0a712870c9a` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed130.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed130.json) | other | 663233 | `6ed5cc020a9818849c0ed46a4e425b8cedc6ee0445fb18670a701422d63a820d` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed131.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed131.json) | other | 711099 | `2626742d6f8a340fed67e02a923424e4b688d9c057d9e20f637eb27cc5b4f7b7` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed132.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed132.json) | other | 698039 | `8fc6259623d5cbba0c31ca6a92ae2ca5c8ce9f526c9af5398dfa06fd184b4fa8` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed133.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed133.json) | other | 678816 | `6460d8674e80b71f115aea394fa99a42e32ee9eae9c25044b32839e143cdbcc4` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed134.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed134.json) | other | 680926 | `03b3451050ebe797727230b0da703d4994ca7f64b83e08a7147c8b4232803f15` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed135.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed135.json) | other | 722872 | `d92e8b3596616af3a0deae3cf1bd7f4e13b95e52028f1a2c50d0c30c5efc2dc2` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed136.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed136.json) | other | 711967 | `42366adfca803e399b6be93e2d52c1d497f42ceaf0d6c40c8fdaefad6792e608` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed137.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed137.json) | other | 703657 | `e0027cc96426ae1fd49062ff55a3b89a19b6a5e826aa0fdb9abfddc9e044d2b1` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed138.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed138.json) | other | 688058 | `b87cfe4054f0993942302b1d43b30ba75a30006cd990bbd2672e56232542d9b3` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed139.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed139.json) | other | 711191 | `a0ce8fc940c649cc67a809a37121e89e964dd0050dbb8262402e7437b1aec6de` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed140.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/w2bud_kwin_confirm_cellkw05_seed140.json) | other | 708909 | `17404ab8431c8031e108e5761c711164201c0f61963c1eec639fdad2aeea96ba` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm_matrix.json) | other | 50842 | `2d1df03273e38501dfb7fd859b8dc59aa3a44e5ce780fd9e11e651104c764bd1` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_matrix.json) | other | 51505 | `6cdf7bbaec08102d4ac4cf796f3560c2cb5391e184131b87039695712631f5a4` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_eps10_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_eps10_seed1.json) | other | 576706 | `d2aba07a4034b6d7a72c5e13069085adb35aa382c4c1fcab9fdff149ffc68575` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_grid40_s300_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_grid40_s300_seed1.json) | other | 202457 | `720964b24a4925c944c9820338dab9137b50d0a8138f18dd06f3f9b2c063cecc` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_grid48_s200_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_grid48_s200_seed1.json) | other | 122933 | `8f0924e0cd188131694b9e4203d70b77da9c8daf343575ae6288011aadf166ee` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_grid48_s250_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_grid48_s250_seed1.json) | other | 164693 | `4395c85f7e3125fe998141490db06584dca7b6c7fc605716c028f8b6a78ae993` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_grid48_s300_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_grid48_s300_seed1.json) | other | 210900 | `d4686938f14e648da49bc84b9f32c2fb453025686e8dc88bea0bd90739b890c7` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_grid48_s400_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_grid48_s400_seed1.json) | other | 341916 | `7aacb84071cda6d5b756ebf27236ea05fbe22372e0e8b81e854de59c92411e7e` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_mut015_eps10_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_mut015_eps10_seed1.json) | other | 1017431 | `8e14c44632cd2e3d31e0718f9f6fd5bdfa750f0073e881dd5f538c7ba3c524e2` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_mut015_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_mut015_seed1.json) | other | 1026188 | `8bb661a7e2be61c83c5bdbf976cde514bc9c7fa4a945d957f0a041be71ec147d` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_start100_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_start100_seed1.json) | other | 631415 | `4beb78179cb003a549c9a3a2980b0f35a426a56573ac2d7ce8b05031a44dbf8e` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_start40_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_start40_seed1.json) | other | 637938 | `153996850521fc97c418a0a6e77b30cc8d2fb12d4973a3c1d0795663728d1862` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_steps150_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_steps150_seed1.json) | other | 87300 | `110c54af4c3cc5ce3237694e59bb3cf08b9445dea204100c68b94e0a855ec6c6` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_steps200_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_steps200_seed1.json) | other | 120644 | `87a8261d0a859366952176302efe6199e64630511b860957e069bbd03ded99d9` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_steps250_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_steps250_seed1.json) | other | 158987 | `e85d64cbf10da973caaa3eba410dd8299c66b2510f40d6be4cae3892b873500a` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines/pilot_steps300_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_lines/pilot_steps300_seed1.json) | other | 202456 | `81c92c84cd5b9371310cb867d00cf7ff0e74ab705dacd03ebfc4e10ea9af16f8` |
| [`morphogenesis/experiments/E09_pond/w2bud_lines_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_lines_matrix.json) | other | 8338 | `7d12ae02426d3ea7e1db9ecedc237a447ecef390dd4f7373b39af37aa0f4a8f3` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_crypto_seed171_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_crypto_seed171_heard.json) | other | 7205 | `6f10e7317e0c086567323596fd5af09d38fba58579e6ee9796013c6b21d26593` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_crypto_seed172_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_crypto_seed172_heard.json) | other | 7306 | `9fca6dfbd33b6736009b0d7f26b81048d09ad2a1b263d6ce92f61ce7150e031a` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_crypto_seed173_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_crypto_seed173_heard.json) | other | 6785 | `ce5f9ca5e0cce4dd52b1fd075711f427b0117b1923dd943d8a9518f960a08bfe` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_net_seed171_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_net_seed171_heard.json) | other | 8370 | `f174a8e6ce8116b939897396eb9168d8b4e70abd804cebf0584378f0d3bf0261` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_net_seed172_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_net_seed172_heard.json) | other | 8396 | `f14b4ffade66944e724c8484b94cec3037eedc56c2b171b5b39e0802469a48c8` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_net_seed173_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_net_seed173_heard.json) | other | 8221 | `de652d66480081f1b38957cd966765809b1a496feb660fe2c6124ecd1c38ada9` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_system_seed171_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_system_seed171_heard.json) | other | 6870 | `8a4717ed2507b90baf465cb82ff283ad3aee0810ae59e132f0119df34cb8290f` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_system_seed172_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_system_seed172_heard.json) | other | 7474 | `e6e259688000798ae73877ab0d963589aa759b802e671785667baca08d6888ad` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_system_seed173_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_live/dumps/w2bud_live_system_seed173_heard.json) | other | 7166 | `403af2658ee93b8071fc7307f0a73eaad5ff034b382bbe98a6638a86c39c7184` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_crypto_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_crypto_seed171.json) | other | 630484 | `2f61524b7763bcb85cdf29bfc0e7dd244b3b419e72f47000cb480bc87a312483` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_crypto_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_crypto_seed172.json) | other | 598541 | `90555f89dfd8f6cdac338f8ee00aabc6c25e97e3323107bae2046adf6ef4f67a` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_crypto_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_crypto_seed173.json) | other | 590941 | `9b3e52c4e2e9adc894d9e4cb33a42b332d26d638e561e38627f5c5b2af081c3f` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_net_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_net_seed171.json) | other | 619874 | `1c6abc0fb692c40f5f27762b97c23818c76652afb485333cb84967773fc43610` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_net_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_net_seed172.json) | other | 615647 | `773536fc61cba06d103f4be151025f31d88fcc0676be9ebe68bd30210bb3f709` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_net_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_net_seed173.json) | other | 614514 | `9b515e1265f9da0713e77db436445a9eab8dbb77484f8acc2eefb7274a97ab75` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_system_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_system_seed171.json) | other | 616022 | `74a91ccd8f902d9ab665911971ba4ad799d34c0a78be05307312a8757a6fa35e` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_system_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_system_seed172.json) | other | 585167 | `df1f35f0a8abc0250e41f38215e7d72b49a4a4e0e7315741cde22bd3f45d9977` |
| [`morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_system_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_live/w2bud_live_system_seed173.json) | other | 618895 | `b86f9d4be6161212649f2e5e009f0cfeb79179643d8ce9ab5629b1205f38e4c9` |
| [`morphogenesis/experiments/E09_pond/w2bud_live_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_live_matrix.json) | other | 17317 | `f714fd5056a29931395a61fd71681968df16bd5ad1b6464d22332f6b39e320c0` |
| [`morphogenesis/experiments/E09_pond/w2bud_live_rhythm/dumps/w2bud_liverhythm_net_seed171_heard.json`](../morphogenesis/experiments/E09_pond/w2bud_live_rhythm/dumps/w2bud_liverhythm_net_seed171_heard.json) | other | 367 | `de6a98e4ac740a0fd0b1a0e2aadef5403df302eaedefb56265dd1900786d6f6b` |
| [`morphogenesis/experiments/E09_pond/w2bud_live_rhythm/prequel_not_wired/w2bud_liverhythm_net_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_live_rhythm/prequel_not_wired/w2bud_liverhythm_net_seed171.json) | other | 620326 | `23303a44a047a6431a88f89be6a842c10da86522bc76d69d2dfdb71a1bc1a76c` |
| [`morphogenesis/experiments/E09_pond/w2bud_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_matrix.json) | other | 35574 | `faa4013fac8727fd6991b52f5460b58fe1776848c42527d9a765b140dc8ee046` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed101.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed101.json) | other | 597189 | `27b59f49865027df3ce7ba337c2a177e379dffdd46a8bd4b0830c4db98f68799` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed102.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed102.json) | other | 603936 | `2bf73d26a584ce7b4f99311b4ffd37fa6dcbe045562694c076fc2d86a9d36f43` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed103.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed103.json) | other | 620544 | `44bfb20ad88644b21a326553cfd89c18a51d911f6ee6ac13df07d5bae759513e` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed104.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed104.json) | other | 630444 | `78568a6e0a476fde3ffd06df061349ea978964b76ed0b088d4130c3229c780d9` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed105.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed105.json) | other | 619562 | `0c4f640fb24c73c2de21aeb30a6645f269a7f62f50618364d99b50ae0188b339` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed106.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed106.json) | other | 603790 | `a13c6992a16a2976fa6240ef4db8387fa76ef55638ce10b2c137d8e8966d7270` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed107.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed107.json) | other | 618903 | `6aaa350191d38e0d614daf0fd825d9de9c887b3b77aee4e21e3d3e641b93d3fd` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed108.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed108.json) | other | 606674 | `f72c4f91114a5e691f8e35468482aa7cdea0a13dc3a4b5e3bd7220ea1942de4c` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed109.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed109.json) | other | 606054 | `fe7e8efbef5eea2369064d8dc18af359a632d6a70c429b6a7b184e0c8acec096` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed110.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed110.json) | other | 592249 | `748a9514d596bf4d1f4fda2df1dd2453ae12fd118fce29abc2f0e2f2e328e817` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed201.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed201.json) | other | 578358 | `993407067f6af49c60feab379cda277e0039b7a8f6a98512157bb72b177a4d20` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed202.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed202.json) | other | 604235 | `d326e4b365a925d7fa9fbc134b8894997d1d8d18c9a773eed3d1466bd48f3309` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed203.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed203.json) | other | 638278 | `89bc729161d388e6f810fe6f7c9aa92a3f00c52ca9d4dc6cb599ca529993a06b` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed204.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed204.json) | other | 595354 | `1d2cd978b07e35c67b704d3fcbc28d0852547be370e6df66525013efac9ddeb7` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed205.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed205.json) | other | 623951 | `ebb1e902f977e72308b831aee473fe257b50042b00fd4230081a5ebf57253380` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed206.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed206.json) | other | 609485 | `ab7a70338f24d07a671200494c798993a4bc29da34ec298c9a44b3c1d58dde73` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed207.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed207.json) | other | 601004 | `6457a55da7b1a39984a24d46507e7541278492bec7d6b885773f703bd77b68ba` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed208.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed208.json) | other | 611835 | `1bd029895692d9ebe49af040c9cb89d1130aac4cd90e84836d7ad2183660ffa7` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed209.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed209.json) | other | 601020 | `66c6d8b8cef58b58dd1744fd67f2c0739d6c5b1a000816dd47fcfc760fb88bb8` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed210.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed210.json) | other | 605388 | `53bc8ccd3dccb451a8eb9eda5e450467ed8bc7610aa07e1947d252fefbc7b002` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed211.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed211.json) | other | 592883 | `01146d20599cf97e676c727f08ac44a9eef31b3ebd6aa332a0cbb7f857f36f83` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed212.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed212.json) | other | 610336 | `7a5823a4e5eae3cc195b5dc4b7dfcaaf76e51c6e9c8ed47ff976a1c502e7ef42` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed213.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed213.json) | other | 598025 | `690fd85ef653f16e937aafd443bf5c17f1983527f4f2b91943a97276b7536bdb` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed214.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed214.json) | other | 623313 | `81e5d5fc70bc9291b276c088bb122b99a30a5a1c77e6b8149c730fb186869f1e` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed215.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud/w2bud_onebud_cell_seed215.json) | other | 619006 | `d0931f71f12008dfa0ab9674e25cf32e153ca0159aba13a181a2a88fa260673e` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud_fisher_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud_fisher_matrix.json) | other | 8582 | `a01fc651714df82cf30c067050cd3167fe9d87c9be3d6b4e819b28c2abbac12f` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud_matrix.json) | other | 42072 | `b541674c981b67ff8d52dee397658613bca60d63331be2d5bc7333e35c5ee50a` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_deaf_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_deaf_seed171.json) | other | 531076 | `fbe58839ee6eb601dca376ce30abf6427ee74917693bdc04dcc1e5191ead06ab` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_deaf_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_deaf_seed172.json) | other | 499152 | `b85804328799cdb4e502a35108b0c8bc99b4967e4c9af9b24aaa77815c2b61c7` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_deaf_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_deaf_seed173.json) | other | 486560 | `3e67ced2ab82eff8b7b94e84bb83673f9345c8065f78fab084b9936298bbffe6` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_seed171.json) | other | 524511 | `4791b8b9fccd66c267882bc76edc564da85a7fa70c9b87e01028c0797ced57cc` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_seed172.json) | other | 508158 | `d5bd94c571be4bc5a13b1404f330bcf72a0952001ce45ff5631922ff39e69ff0` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_edge_seed173.json) | other | 494047 | `c0ca76d70dceee7136d07199c834b2ad353651bee8a15fbb24021582ca98310d` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_global_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_global_seed171.json) | other | 518198 | `9313c0869d3f3c87f6317f35cfaba52d3c88d815c2b316c300d028e10312eb92` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_global_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_global_seed172.json) | other | 492890 | `a2aa386dcfd188fc4f7ed2d63d57ec5191a98f0ce03c4a2b227c457964a9c096` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_global_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_global_seed173.json) | other | 510213 | `8d18936cc99c250f8a9e17c785c45f7a75b743ea8a6f5130c7498019fcfc24c2` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_off_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_off_seed171.json) | other | 530698 | `1e8e343a7f5214a746ccf022d4177ed52cfd20b9bce48a9639f3612c29b51acf` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_off_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_off_seed172.json) | other | 498776 | `4e67dd46ee9dbe47cbd63ef8335a4b991963286839bc8a834e8d9c88fe786ee4` |
| [`morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_off_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_org/w2bud_org_off_seed173.json) | other | 486183 | `3bac669219f5ac9f2cbf2f82b4ab9f0fff68464667e29907664548c21906a3e1` |
| [`morphogenesis/experiments/E09_pond/w2bud_org_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_org_matrix.json) | other | 20902 | `028c191aac6291747d03f4f771db66a1a2ebbc5991929f38147ad65414d8df9b` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/pilot/w2bud_pair_pilot_pair_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/pilot/w2bud_pair_pilot_pair_seed1.json) | other | 503310 | `83f6a3f68ece5308a2beeb99d7009a06666e602df678358b321ebd1eddeb9a38` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/pilot/w2bud_pair_pilot_pair_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/pilot/w2bud_pair_pilot_pair_seed2.json) | other | 511484 | `0b7949faa879b2c43b1aa11992a195598f1b53ab5fd5492f126cf1872aa71f9c` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/pilot/w2bud_pair_pilot_pair_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/pilot/w2bud_pair_pilot_pair_seed3.json) | other | 523614 | `6ba294b1ecaf293d6f46f420560b4e734310b79bd403247b4a67c023d1cf2519` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed101.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed101.json) | other | 506777 | `08619bc8a194f4f36a9e77eda8e1bea752b0e02c2765b87926df4cac63eb42a1` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed102.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed102.json) | other | 543909 | `e20b87ff5cbeca66bec19bb7187ce803cd01e63cb85ef29c553e6e7c1df90e37` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed103.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed103.json) | other | 527278 | `380de4a0809a28e84d5007a3fc8d570571a4caa622c583573a238ace1b807a8d` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed104.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed104.json) | other | 531287 | `23f1c7f91f5c59ea9b88675cbcdc78a74e48ee92a2b05d9642de3a210a8db9b8` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed105.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed105.json) | other | 512306 | `dca018db26c758f8d774f554befc4422994cbe053fd88189fb19a538bccfca7c` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed106.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed106.json) | other | 502858 | `ebd97ec057aefdd9a37c66cd29482bac2af2b27908f68390d282917939555de7` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed107.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed107.json) | other | 528659 | `eff6fdfb853a6d1b8cae1fa701861006af6831fc6f57f67ef7c9b9b4dc0a448d` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed108.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed108.json) | other | 530403 | `75ce612768a574ae184718d4b379734d5b52ca9f55cbf656dd18848a0ebc81eb` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed109.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed109.json) | other | 516703 | `465aa48709cba88ac074e3730b6d0babf7184ba5ed8677682d16b3399218e08b` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed110.json`](../morphogenesis/experiments/E09_pond/w2bud_pair/w2bud_pair_pair_seed110.json) | other | 515841 | `7697f7b0ce7850602051db19c5cc9756abb8ff81ff7eeebed7d4ac85f1271bbc` |
| [`morphogenesis/experiments/E09_pond/w2bud_pair_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_pair_matrix.json) | other | 20358 | `35477e5f757a45420e041288a35a6ed1afa9bb651882045d48e413c764734b8a` |
| [`morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed101.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed101.json) | other | 528777 | `bc55def6f2acb7787418848fc0dfe1f14829180823cfca6d47ce1d523a443941` |
| [`morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed102.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed102.json) | other | 507783 | `8bc51600347340ab083be0ac1d566976247d99dc2931a465319bb8f1429fab4b` |
| [`morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed103.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed103.json) | other | 516189 | `99a92c19f0b449603935ad69ca4a684cd59eaa0643c3caf41eed678c7910802c` |
| [`morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed104.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed104.json) | other | 524621 | `b26c0e3d742c7213535528e96f582fbaeecaf8ca0cea35f7b603d766cfb946d5` |
| [`morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed105.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed105.json) | other | 526969 | `1c01e7ad205d19dc5a1212a6b5f2774cca4412be71479e353e54d0d4a8e77afb` |
| [`morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed106.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed106.json) | other | 519140 | `364549241f1f27f024c9f87ca1be2e8cab3eb3e11baeb91b6deb3326ea4610ef` |
| [`morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed107.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed107.json) | other | 522629 | `81d47963c9fc305b87b3d7ed8834eb56ce66167f6dceb8f57d7496b213a80a41` |
| [`morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed108.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed108.json) | other | 508797 | `f6774185a8abc3c98439e0cc6e9bdec20c08a64a0d1f9e46764c897d826b717a` |
| [`morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed109.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed109.json) | other | 511337 | `bab3d50c273cc5ee1069dee666ca92983752a78943a62fe2bc3b0c12ce4de686` |
| [`morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed110.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany/w2bud_pairany_pair_seed110.json) | other | 515345 | `5318e45fd47c1ac945580fa549d8f5c6a41fc0c86a93041391c35effcf82fe3e` |
| [`morphogenesis/experiments/E09_pond/w2bud_pairany_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany_matrix.json) | other | 20385 | `566831266551321a38bb018e2e7075257d4458c9a8d0a88ad72fa4a950e95cb1` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_bud_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_bud_seed171.json) | other | 523407 | `9f08761307dbe423cce090e66c342dfe524554a25b89fa0761b595a076d5f88f` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_bud_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_bud_seed172.json) | other | 505436 | `c5e938a3bb13d3713f617f2d561d65bfd9f38c6d96ee30e4b2a918ece2217b44` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_bud_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_bud_seed173.json) | other | 483539 | `0a27e0734a11dee37fdc0babaed0883ae3d0926941383df40c31b6b31e4e5df2` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_bud_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_bud_seed174.json) | other | 478685 | `abe267a4aae82c87140f092a908aa060aefd227c7d56eb8867435a0261755747` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_off_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_off_seed171.json) | other | 530715 | `1072202dfaa008dc2d7af678a57626595371d67beba6bca7930ff93d2cb3ebb2` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_off_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_off_seed172.json) | other | 498792 | `baf687f2892170158228f800dd80b05e0731bdd2d4893a4cdf1ce22f53be7568` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_off_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_off_seed173.json) | other | 486199 | `782ee915d97600a5d70d631f7324dcffbc9cb2dd150e5e394a416e11f8e8cf17` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_off_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_off_seed174.json) | other | 481378 | `8558248877e68716f6ba2b5d8c7b0489b96bcfbc4d4e4822e77ca3500c837a70` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_sham_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_sham_seed171.json) | other | 531484 | `f8749c71994121a0c2a8ad4272ae9a64d3f897613a8994ae2d024d2e2aa5e1d6` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_sham_seed172.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_sham_seed172.json) | other | 499708 | `83e7e5797edff4a0a2890c7eb3bbd24469bbaeff40381bc00f949c79af9f7012` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_sham_seed173.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_sham_seed173.json) | other | 487253 | `015c54eec37c44f99035b7a2bbd44cec9935049ac1028dd518891d99a3cc764d` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_sham_seed174.json`](../morphogenesis/experiments/E09_pond/w2bud_patch/w2bud_patch_sham_seed174.json) | other | 482575 | `b691c9610e1291b0b744c152251c585381c38e137fbf2b6d18ffa0d5848ef26b` |
| [`morphogenesis/experiments/E09_pond/w2bud_patch_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_patch_matrix.json) | other | 20941 | `3d83b6f0bdcdb12d9db54a6900eba9eecb0013ba46cd15aba322781401d542fa` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed1.json) | other | 508361 | `394f85ac868a59c87df4f8ec45fe1602e6893da3f8e8c49eb9a9288b8119edf7` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed10.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed10.json) | other | 499460 | `9cde27caeacc45af199833fbdaa66da19644f552f78ae3333f2a0374809e7db0` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed2.json) | other | 520573 | `cb040a990108f2a2db9f0f70df89e830dbb1820db9f484798eda2c4cdcab4944` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed3.json) | other | 494169 | `a6c3caccc64feaa1bac7e4cc29fac02782188c75e40541450bf09e73085bdae3` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed4.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed4.json) | other | 518755 | `9a1f8defb0962ed09b9e943a66068f0a8b26303f6e345dc9c2e3085a077f437e` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed5.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed5.json) | other | 509457 | `2474f09c7c75f549cbe81883899e716a3c68af92dc857f4d25a94695af1628f2` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed6.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed6.json) | other | 491644 | `abdf50d22d6e2680a39d8617002f715f20893687d274a4b3401474bacd28405d` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed7.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed7.json) | other | 513063 | `2d5fed30c7ff323ec2b42f734a31d16bf870421ffa9b41ee1cea84e2b2e01413` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed8.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed8.json) | other | 493145 | `6ae71d901ec709066c0bed05c079db4b56859ec3242ea3dfdd765b6d2145ee88` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed9.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cell_seed9.json) | other | 493586 | `862475628ed99785dc62fdf01143e98439d1581207446b21a32f8156c439648b` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cellq50_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/prequel_wrongparams/w2bud_quota_cellq50_seed1.json) | other | 497608 | `0a214f0da2ac53b3d1c55a144b62b13b7ffc3cdad7b575fda62b1d34579ee4ee` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed1.json) | other | 534263 | `e87a28fb8eccf2870ea4b4a71b471e029981bbf0bc9c0c191bc880655f8c4a13` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed10.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed10.json) | other | 532278 | `62816eac4fad1899cabeb29bbb565dfc21ddfba386707f58feaa01bd259bf4cc` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed2.json) | other | 527577 | `9c3b6e0a824c9579db41e60840770e6a602224c41ed51a9a627940a70f02d76d` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed3.json) | other | 530422 | `397254a6e4d2e42118469a242d409592ce65fd914fdd507f0fd1cba1cd94cdf5` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed4.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed4.json) | other | 534921 | `5c48c8e2de00e46e2b7acf20e13c9dd2e1d2445c097b097d90e481c358ba14e0` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed5.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed5.json) | other | 556621 | `4a3de2000cbc1b550bd474584ee2a32f2424cca971d689bfc2ab72e0677ff9ca` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed6.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed6.json) | other | 538280 | `f0d7362fd851abad6b969df8b9ea22a032bfb1de30b902c870791d0c371d855e` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed7.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed7.json) | other | 538423 | `0faa3700669e86ef70054bd68f24fc7be313593d3a1fdb8264bde366ea3847ee` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed8.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed8.json) | other | 525313 | `3946c5a6b1b3cdbe4f3daec09fb69a755bdae4cf07fd9c7e780f7cfa8785a8e8` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed9.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cell_seed9.json) | other | 511894 | `7f579eb6da42965234af8a6de5ae03099913d95543867011e20ddd0e9f9449ad` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed1.json) | other | 560688 | `95aece31714679e0641221de2d623e9197287fbb37f64bbac5334f03fd558e6d` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed10.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed10.json) | other | 532737 | `0ddc5a7b63c8a82367c5a5e5ecf820262c354ea357b83f1baa631a7cf86e153f` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed2.json) | other | 534367 | `5fecc3118910659a3594b064c79ea40696bde03b949eb9590c8faa7f9baafb48` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed3.json) | other | 545947 | `911832331cc97b338115260f3efb41521881cb39a905e309034c68f9767a4ff4` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed4.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed4.json) | other | 550686 | `f324c0da75bcdf401dac573c882c722e5922c5f2c44fe2dc510fe47c3e8b0353` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed5.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed5.json) | other | 529410 | `3eaa65d1e7bfa7c851f80eb4d3d95702c2463fcf4098c5bfbb7fdf213d4481a4` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed6.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed6.json) | other | 517833 | `b97bbe28c1793bc77fb9f5fb803699bf846bf4a412544e711bdbf128303ca639` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed7.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed7.json) | other | 522455 | `d6eef761a089ba9794f0dc93a2c3d557bb49b068111db4ef2eff8a1490136ebb` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed8.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed8.json) | other | 532755 | `302778c8fbfaec4546d9de6e39c2bcd9f3dfc75523e51bb531551929ac0ee40b` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed9.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq30_seed9.json) | other | 531168 | `6eda7261b618fd165e8172c1f109103efe120d62ed62cd9ee0184186e93b0d93` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed1.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed1.json) | other | 535648 | `0a2ffd78789e7c0a6634e4f7d8dba6fa84b74d20c8d57cc01020704f11e93fdb` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed10.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed10.json) | other | 547755 | `0fea68194b586119b34201542e9b50b68b5383e384733455c18c3362a3a5b7c0` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed2.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed2.json) | other | 554903 | `a88feb9dc5c520c4b6ddc19978e29447149f69d69e7989b254b66940e91b9738` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed3.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed3.json) | other | 544153 | `ec4f09dcccfda08dc14003716b1f744d9a7b4493656e6105cbe7dec19123df8a` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed4.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed4.json) | other | 540272 | `baec2126d05d513990605c8df7993b70bd7fc4b8eeaeb3dd6e1e2c7748afff1b` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed5.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed5.json) | other | 543002 | `5eaecce64ec37e267c92ad9e58b816caf96ba98855e3329a3f831ca865bb2acf` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed6.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed6.json) | other | 533612 | `413dd32eba7228ec69fc98500c1bd41e76ea5885e442998a484716eaaf7caf15` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed7.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed7.json) | other | 522350 | `7e202460889ef218d2719103e72b1321c31983c282014102c34354ac04637494` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed8.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed8.json) | other | 542573 | `1c303bc7479604a989eb8682bd8623dacdd00410d8e41369c6ed7c2efe03c04a` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed9.json`](../morphogenesis/experiments/E09_pond/w2bud_quota/w2bud_quota_cellq50_seed9.json) | other | 531168 | `36d4d78d76c3eef658520fa48b6e2723f3e9448994e396d8ae5c52983a01d7cc` |
| [`morphogenesis/experiments/E09_pond/w2bud_quota_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_quota_matrix.json) | other | 49896 | `51d276e0088ec188d5df9c0d4062e1d144acf81011422264872b96a3595f3844` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed101.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed101.json) | other | 490971 | `a9defc29ba7b13676c43da3c34c31f90f212cc6756822163acffbeea232a33c8` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed102.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed102.json) | other | 515755 | `9da9ae5accd87697c17c6719ebdb0018fc50dc451be4b37df383f7ddfe2ab141` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed103.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed103.json) | other | 536240 | `a002153355336421f43c2cae07717ba844aad2c766684ab90f9b1d03ecc5ad7f` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed104.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed104.json) | other | 517432 | `0ebd1be991d4b90ffd75dadb386ae0a11f479d618f9f4f1689bfe8ea5fbb8895` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed105.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed105.json) | other | 460874 | `2b691397258a52cf2954f2927792733e3d8f7ba0396b4fcc3f874f6542d21f61` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed106.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed106.json) | other | 503994 | `81580558a0ba5cd41678c6ca9ef2b96457fa57486ac04ec252c759c15c72ba4a` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed107.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed107.json) | other | 368011 | `7b7f51451e031fcb3798e4f4d658dcff115c9cbaa86a254fd7fef0ad7343be39` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed108.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed108.json) | other | 481128 | `8624ce2f08fd765c788a7fd188309e6a2bb4e15971e982705a20be6b7e0c1290` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed109.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed109.json) | other | 384685 | `9f214b1244dd9bc9e3b88bd76d50d7109bd400fe2a2a35f9baa2f09d6a194f5c` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed110.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches/w2bud6_cell_seed110.json) | other | 547497 | `ae573afb22cb1a8c5655a12c4af32b538655d960042e13971907816829978566` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches_matrix.json) | other | 19553 | `0ca0ad1200e14b690363a268eccf61c7e0a801ba3bd26c1136207b3595fd5589` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed101.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed101.json) | other | 509708 | `32ea73abda2290a539d2150fc560fd15eef04281aef281e662bda7bf5c5be381` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed102.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed102.json) | other | 542383 | `90d0752de2d092e9df04fc3be35627a26f2cfa30cbe21d4edcfaf87af06cb2e3` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed103.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed103.json) | other | 525250 | `f58828a6d7deae0a63bace298fe0045b0a444732509f416159a54ac51771e139` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed104.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed104.json) | other | 557991 | `7ede8e4bf735491ec462f5071a781f27a54f272f3ea3708fdfe2a24b570c4a10` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed105.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed105.json) | other | 507473 | `49122c58838588accb6eb3b1b25139715f2100618e8bcbe30d2efd92fab70cfd` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed106.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed106.json) | other | 532545 | `33d86aeafc6284c77b41b70fc4c4c3201ce9b8fc68a8d8c637a0d4c9a31ff986` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed107.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed107.json) | other | 534971 | `44b3b9ec458eebb4fa08c531a19d00c58a4c7761b714e9249b3940b6f7c7f506` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed108.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed108.json) | other | 517756 | `dd78211f3fe81a9a8297c83fe24a7c6f4127f93a6550621cd685acd529f3923a` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed109.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed109.json) | other | 546037 | `3335b0405d332941c419219ce7b5fe06e30a03359583a52aeaa30addd91ef359` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed110.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_cell_seed110.json) | other | 535054 | `5de881293ec51a166a8ea602431007b0a8325a5b0af496586b12f2ab63e51358` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed101.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed101.json) | other | 543497 | `95c7f5c3f92baeb5470cabcd8a1dfd3f62b09ff3e4150963ed8caf7b76865510` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed102.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed102.json) | other | 544786 | `8cff97051eb8d75db89ff20f0cc8884ff420e191756e98d187ee8598011e4ab6` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed103.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed103.json) | other | 557724 | `27ebdd61e199f9c5342ae8f7bbcc093b917ac2cee4bf6f7de5702b2232ef004d` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed104.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed104.json) | other | 553488 | `a581adfd6c47224241cffe6c42f26a2093878ed04953cf8a30cb73d6c5dd6a2b` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed105.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed105.json) | other | 549356 | `87e6d2d260967d6545ade0697a8e40b7827e9a9e3b4acec21c662972de1f04e6` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed106.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed106.json) | other | 552117 | `ce5e3bbc247fae9ac2987a82780522faba0cb8c2f28bfafee53e37ff9ee646e4` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed107.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed107.json) | other | 535492 | `362e111aa5809d217f24e35f5915c93cf6e3c1488eadb36b6b3754707dc73c67` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed108.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed108.json) | other | 537614 | `7246e2c13314695b1738a2f19af98eb31eb1b6aaae5a03eac1964ea1021c87e5` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed109.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed109.json) | other | 556842 | `98a1e8b1c3752d13618e03db33c41437d4ce517c0aaa06b814581e39234b979d` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed110.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform/w2bud5_colony_seed110.json) | other | 541663 | `d07c4f327d5468e02b61605b089866edbb7ed28f9a35e1f08421f2ae2f39b039` |
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform_matrix.json) | other | 34369 | `b89ddc9b8b9fba402d40e58e7188cd3ae8b3cfef4d61dedbb033fa4b1b0554d5` |
| [`morphogenesis/experiments/E09_pond/w2bud_stream/prequel_premise_rework/w2bud_stream_cellc_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_stream/prequel_premise_rework/w2bud_stream_cellc_seed171.json) | other | 619963 | `6b6dd9c7a577bf3a9027562092f1763b530bdb82abf147b243de366ae87416e3` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed151.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed151.json) | other | 453871 | `aa6ec01c19849d3d1f90bc966781ee883234942ff9298a52a08726de97c059b5` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed152.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed152.json) | other | 462708 | `33e032d34cfa97b8318be76ff76218353706b7007feb1c0bbffad0396713908a` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed153.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed153.json) | other | 467832 | `44bff0ff54d6ad50174aead7973dd440bfde2c321eebe6c1081b4e9648256289` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed154.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed154.json) | other | 508681 | `587de917db5776c24187496bf954c67933d43389d46233497cf563f77921b6b4` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed155.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed155.json) | other | 467729 | `78a98f33f940ae4b445b663418bc7e0fdf20f3a923b38389f35a9b95a5c63f3c` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed156.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed156.json) | other | 442999 | `14323c945af0f775298952b496f26222d8e3961001482592b213ee2fb791c79c` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed157.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed157.json) | other | 484946 | `7fce6f350f400c51f648495edf3db7b74d133927c1098f446f8d41266ea029c8` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed158.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed158.json) | other | 466165 | `16a9a98be96af490d4017c7b09fde924488c05faa2068adc8d2fba1c6ae8a495` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed159.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed159.json) | other | 473531 | `bc2397b5033759e5f6498b20e78373eacc5b36fabecffab960e1b10b6f73fb2a` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed160.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed160.json) | other | 475412 | `317807e3273f07b6926923e579315e8d5ea010dc40cac8a589f95496adf96803` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed161.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed161.json) | other | 490657 | `6c3dd44322437d8d8c0d7181f1af94d25082c3ed59a225cb89caf27fee11f4e2` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed162.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed162.json) | other | 482150 | `ba241e997a89bf87ac853407a5a9d46ec3497063db08716b9f2def03671e681d` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed163.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed163.json) | other | 496336 | `3cdbcad66085b78f9b2ca0e3c8014c98542fc20affa53a870e58f6092be3d571` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed164.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed164.json) | other | 462987 | `b42aac88cb4aa349e9f574f19c5de4a3440bd89fa2f864496580d2ced9aa28f6` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed165.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed165.json) | other | 491497 | `ad0e8600079b927b83822ccff72286952f15dcc5fc4f954bc917e796ebe4c88b` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed166.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed166.json) | other | 430495 | `ba6ac17df684ade99b14246980ce9dbe65b7ec702c842ea861ab8fd8b3262985` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed167.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed167.json) | other | 481813 | `213b5bd9a69658ead929a4bcb189d4327dbb016d633133faae0998124167415b` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed168.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed168.json) | other | 466369 | `97f36e1a6c40e99501936708c81d8e8e7f9bd5b1a27101ca801ec18684b7f2bc` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed169.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed169.json) | other | 513431 | `c1552f46935f6b1aab437193f3d36147910d92b32d3d1703a00892aad93c0051` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed170.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update/w2bud_traitupd_cellupd_seed170.json) | other | 442695 | `5eeee0d3599f446835ecf6a97f58a69c4b27c666eedacaed1a00b505743a8119` |
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update_matrix.json) | other | 34428 | `74b0e549fe70652ead5f37dd68adb897658ad482f55a8654e559b84d373bccc4` |
| [`morphogenesis/experiments/E09_pond/w2budd2/pilot/w2budd2_pilot_cell_seed1.json`](../morphogenesis/experiments/E09_pond/w2budd2/pilot/w2budd2_pilot_cell_seed1.json) | other | 605399 | `0f0087cbf74ad6b6c21327492a16fb167b540a6bc23e32e0d799f4905febc59a` |
| [`morphogenesis/experiments/E09_pond/w2budd2/pilot/w2budd2_pilot_cell_seed2.json`](../morphogenesis/experiments/E09_pond/w2budd2/pilot/w2budd2_pilot_cell_seed2.json) | other | 602952 | `a196907aeea6fe12ad17a4fec13cc1352e14934c5e3ab49b9535eb92f1afcae1` |
| [`morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed1.json`](../morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed1.json) | other | 605398 | `abb037655b950b420579c206b009b0f0ffdb096b1710462f1eccd9fcc33c7159` |
| [`morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed10.json`](../morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed10.json) | other | 613747 | `88ca7a3bd0207dc7bcd9d75349e4e8614d90633a33053b133cecbc4450d854ee` |
| [`morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed2.json`](../morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed2.json) | other | 602952 | `bc4c25a456f3f2825c771adad7826b161d3ce373880e37d0d69c162f432bf402` |
| [`morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed3.json`](../morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed3.json) | other | 600760 | `40231f3018b3d2e47525b6fa416b6d1cfd707dee31a2f3279224ae6c05647b8b` |
| [`morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed4.json`](../morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed4.json) | other | 594990 | `fde09f2db213d95dd65ac1ca2028bc8e9d1cd9c64f20bf20a6bcd55682f7eb43` |
| [`morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed5.json`](../morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed5.json) | other | 617604 | `28341b5fbb08784dcfd62243944ec20b0c560f6599d3f40d03f31f0be73339ac` |
| [`morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed6.json`](../morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed6.json) | other | 608741 | `f2917a973292ff2a92f1ee77770f7376cd03ca51c857ec7d50a2d36015c2460a` |
| [`morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed7.json`](../morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed7.json) | other | 585356 | `4b7889ac94f3029a829bb119a990f6b16943a322c05ad8fac3fd438cb6f8836c` |
| [`morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed8.json`](../morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed8.json) | other | 601642 | `b5ea8775710d80aa112d32dfc45affb1e82f0bc30f8874b99acb57b2a0b6835a` |
| [`morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed9.json`](../morphogenesis/experiments/E09_pond/w2budd2/w2budd2_cell_seed9.json) | other | 614054 | `b6a48f80102f340b9371755a4c3487f64793c1b9aa84ba4756bea47a3a90e21f` |
| [`morphogenesis/experiments/E09_pond/w2budd2_matrix.json`](../morphogenesis/experiments/E09_pond/w2budd2_matrix.json) | other | 20030 | `704d6770506df9771f9d61c77a75daabe27b226fc431bdf520ce21d8feaf5e6f` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed101.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed101.json) | other | 612784 | `25357062ceda5e542411074ab336984ac83ca448537c0ab9faba1588db4e2703` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed102.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed102.json) | other | 609876 | `d3f7ad3fcd9a3fb166a057a711d9212fafd4e73817d6c9a279f1f7d5107e13f5` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed103.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed103.json) | other | 614708 | `779a7032525bb6a305a9ea23088e0f8b2c044118ffbfb6c0ffe6d3c3230eefe0` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed104.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed104.json) | other | 613342 | `05f6c2be23eb823b2fcb161a28f372aff71e3cb282158947b1c0e1842af73d9f` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed105.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed105.json) | other | 585064 | `6822711a31e4688bf2c6a0a4ba8ccd6742cc5a6df89c80087ce82bdaf62d2672` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed106.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed106.json) | other | 592759 | `055eb41c8613b9a7d33e655a6c3b6d79206813f3db9f3ceae2d6436d0739d752` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed107.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed107.json) | other | 609073 | `0ef90d5a1dfac2ca8e1b5547980e50e641bc6c4eba7e271828eff2bcac98f59e` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed108.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed108.json) | other | 614456 | `14f02984cfb0f9ac055410ab1e284e361821ccfc2cb96346e1b8832fc6da5134` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed109.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed109.json) | other | 625596 | `eb99b5beda33a6c197e3f1cd5d24a085d1329240912a0de05eeaa1228faa5194` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed110.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep/w2budd2_rep_n3_cell_seed110.json) | other | 617328 | `bbd332e4e8d533dd27bff73af278d2b131b3e30a1f1d3a87d2cb027df3a6b880` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_matrix.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_matrix.json) | other | 20026 | `b0d137d41f964e74ee73d1d74833463cf9191317df282f97d387353b0b0142c8` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed101.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed101.json) | other | 509775 | `f21428e9085ac736b668ad398f4108a479f534838da92c07d96409bafaafa5f4` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed102.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed102.json) | other | 542449 | `58287d5a7c94887962185a6811946eb0d516b34156248a3d3eea9f12e53bcb39` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed103.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed103.json) | other | 525317 | `eb37ac873425cf717d8184c6d75bb4434252dbe7340358b3b17ec6182770e69b` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed104.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed104.json) | other | 558058 | `8c429cd8e7449861d1aa73a144f18899af0d813fd771300c37731de1ee112c0d` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed105.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed105.json) | other | 507540 | `659d19f56823df66b52bcc8a3c619b7b0d90c8ece51f83a50c9b2d01ad93b7d5` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed106.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed106.json) | other | 532612 | `eb22a56529bf1dc35a32c45e03e604ce48ead202931d0e9d9523830720de558f` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed107.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed107.json) | other | 535038 | `3f854bfc1b6aff32afa033b74f9babf483296518161efa5286d9ac76a74096be` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed108.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed108.json) | other | 517823 | `5c78ab9ea9dfc25520e8f06d95dc9deb32626072d015f10211705ddc5867c55d` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed109.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed109.json) | other | 546104 | `603f4eaafd5ed0d06cb0ba6c732b68436de1388fd8bdc3df7bb91c3d4522ef42` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed110.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1/w2budd2_rep_n1_cell_seed110.json) | other | 535121 | `a893fd2b2b36f8544a146d73da351cdbd8e296245fcdb5211c698697bc19e957` |
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1_matrix.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1_matrix.json) | other | 20096 | `229684a22da6ba99c5576f1b95175a259623e0add218f4fc58a329fab169a128` |
| [`morphogenesis/experiments/E09_pond/x160_memory/x160_memory.json`](../morphogenesis/experiments/E09_pond/x160_memory/x160_memory.json) | other | 13950 | `cd937d44b3057f5c1fa15c365792b380cd17c1871a665c63fb7023ebe9e949ed` |
| [`morphogenesis/experiments/L1_field/anchor_x60/off.json`](../morphogenesis/experiments/L1_field/anchor_x60/off.json) | other | 15075 | `c98010fba220aa974ea88575b43ad6d0565b0e9227640f126e435515b7ce2890` |
| [`morphogenesis/experiments/L1_field/anchor_x60/on.json`](../morphogenesis/experiments/L1_field/anchor_x60/on.json) | other | 15259 | `81f7e7a5c38b57eeeb07943ff98b513ade609a3d26333f566cf78fac7a3cb8c1` |
| [`morphogenesis/experiments/L1_field/e6p_ctrl_s171.json`](../morphogenesis/experiments/L1_field/e6p_ctrl_s171.json) | other | 36336 | `59003b1f272a1f5dd271cbecfe4105c014a3561c99818d323a74650347452777` |
| [`morphogenesis/experiments/L1_field/e6p_ctrl_s172.json`](../morphogenesis/experiments/L1_field/e6p_ctrl_s172.json) | other | 36334 | `dd51fd8bec9b85574dd730a966548c3627b9b6cb84ae571630a7fc72de90921d` |
| [`morphogenesis/experiments/L1_field/e6p_ctrl_s173.json`](../morphogenesis/experiments/L1_field/e6p_ctrl_s173.json) | other | 36313 | `a52e37f71ec7427466b88c6e3957cec61581a381fca9f8ba2eea021a15ef1b75` |
| [`morphogenesis/experiments/L1_field/e6p_ctrl_s174.json`](../morphogenesis/experiments/L1_field/e6p_ctrl_s174.json) | other | 36341 | `29daf75d3d5e89b2f252dc2442f772e328c115718be525ca3f8d673804cb9838` |
| [`morphogenesis/experiments/L1_field/e6p_ctrl_s175.json`](../morphogenesis/experiments/L1_field/e6p_ctrl_s175.json) | other | 36325 | `fbd54d959b8e0ce643c893922163eb94238ffad4373c11a6b01ce01ec5fad441` |
| [`morphogenesis/experiments/L1_field/e6p_ctrl_s176.json`](../morphogenesis/experiments/L1_field/e6p_ctrl_s176.json) | other | 36329 | `87db0731dc0391dc0cda9c05ee915eb27b0305d15fe4d2eda79d5951075fd1b8` |
| [`morphogenesis/experiments/L1_field/e6p_ctrl_s177.json`](../morphogenesis/experiments/L1_field/e6p_ctrl_s177.json) | other | 36338 | `2d152ec029a880aa074f23e8157926d530b7b2e36a81d2023ca5a2a0e50eddb1` |
| [`morphogenesis/experiments/L1_field/e6p_ctrl_s178.json`](../morphogenesis/experiments/L1_field/e6p_ctrl_s178.json) | other | 36310 | `c6d02edd1d52d4ab5e45c8910d78eee0095ef0f9725a3262ab65c36f71bdc3f7` |
| [`morphogenesis/experiments/L1_field/e6p_ctrl_s179.json`](../morphogenesis/experiments/L1_field/e6p_ctrl_s179.json) | other | 36352 | `6ba57b0cf8945b3b3314c551561451d575091d3d85b05c4d47c57b3342e42c21` |
| [`morphogenesis/experiments/L1_field/e6p_ctrl_s180.json`](../morphogenesis/experiments/L1_field/e6p_ctrl_s180.json) | other | 36336 | `63dc8835535d72484b283150976d585567281d8e9f3bf114fe282b7768ea2d7b` |
| [`morphogenesis/experiments/L1_field/e6p_series_index.json`](../morphogenesis/experiments/L1_field/e6p_series_index.json) | other | 3580 | `c6047f2b4383ab4648082a870aa2ba487b5c09e9ef5e9f5fbf54797020d24c68` |
| [`morphogenesis/experiments/L1_field/e6p_surv_s171.json`](../morphogenesis/experiments/L1_field/e6p_surv_s171.json) | other | 9092 | `18bcad27d416eb1aa587b8a2a6fa2483e63da1309dde3ec4e8718cf884a122e8` |
| [`morphogenesis/experiments/L1_field/e6p_surv_s172.json`](../morphogenesis/experiments/L1_field/e6p_surv_s172.json) | other | 6799 | `59ab57fdaf98712bcf847ff651f398cde5cc8ecf1a5cc5c1f3bf56046aced0aa` |
| [`morphogenesis/experiments/L1_field/e6p_surv_s173.json`](../morphogenesis/experiments/L1_field/e6p_surv_s173.json) | other | 8232 | `e4d536fe258dba153f55ef036fa6855a3e9611c05d89003c5910ec71e1b42a8c` |
| [`morphogenesis/experiments/L1_field/e6p_surv_s174.json`](../morphogenesis/experiments/L1_field/e6p_surv_s174.json) | other | 8362 | `74c9431add2af333e1b17aa95deddc2532a0d3be8916d9a9be4576053e33d881` |
| [`morphogenesis/experiments/L1_field/e6p_surv_s175.json`](../morphogenesis/experiments/L1_field/e6p_surv_s175.json) | other | 6798 | `c37847b862e12978a9c26b5ce8d1a8df57869ceb66fe764ac0775ef65e4e2151` |
| [`morphogenesis/experiments/L1_field/e6p_surv_s176.json`](../morphogenesis/experiments/L1_field/e6p_surv_s176.json) | other | 9807 | `89690781656780b4d2aa8d2af393dd9e68423b6c35231ff5caa01adc2a652d5a` |
| [`morphogenesis/experiments/L1_field/e6p_surv_s177.json`](../morphogenesis/experiments/L1_field/e6p_surv_s177.json) | other | 6799 | `521c46cbe1a68f3c2204df14a32cb712cc47e4b2becbf5edb4edb6eb7fb0a42c` |
| [`morphogenesis/experiments/L1_field/e6p_surv_s178.json`](../morphogenesis/experiments/L1_field/e6p_surv_s178.json) | other | 7799 | `0c33df599309785a32b5df234fbc7afc1df7dcabdf0fdaad8333f1c1c71c7fc5` |
| [`morphogenesis/experiments/L1_field/e6p_surv_s179.json`](../morphogenesis/experiments/L1_field/e6p_surv_s179.json) | other | 14366 | `4521ad7427b83385c132bb8f1468e3a34bc147aef8394b9b711e561aa766adb8` |
| [`morphogenesis/experiments/L1_field/e6p_surv_s180.json`](../morphogenesis/experiments/L1_field/e6p_surv_s180.json) | other | 7091 | `aa20dc757743c6ba9e01192cae8f658aefa14793a4b08ca4f7644b69f9254583` |
| [`morphogenesis/experiments/L1_field/e6p_survfd_s171.json`](../morphogenesis/experiments/L1_field/e6p_survfd_s171.json) | other | 15075 | `c98010fba220aa974ea88575b43ad6d0565b0e9227640f126e435515b7ce2890` |
| [`morphogenesis/experiments/L1_field/e6p_survfd_s172.json`](../morphogenesis/experiments/L1_field/e6p_survfd_s172.json) | other | 23018 | `55b4f94c31492cb08e5039e8fb01d9ea948859b49adfe9e23904fa351c2c7070` |
| [`morphogenesis/experiments/L1_field/e6p_survfd_s173.json`](../morphogenesis/experiments/L1_field/e6p_survfd_s173.json) | other | 11504 | `a262164748ac2968e342ef66f740801eb1bbaf5f073f8d59125f2db8631f4157` |
| [`morphogenesis/experiments/L1_field/e6p_survfd_s174.json`](../morphogenesis/experiments/L1_field/e6p_survfd_s174.json) | other | 12171 | `c30100c729066ff13f86095e747b16707171dfad46c26506d50b899707327f8f` |
| [`morphogenesis/experiments/L1_field/e6p_survfd_s175.json`](../morphogenesis/experiments/L1_field/e6p_survfd_s175.json) | other | 10354 | `9f017f1d84a0e39b2e4f109175af84a67beaea27158e11b2bbfae2c813536839` |
| [`morphogenesis/experiments/L1_field/e6p_survfd_s176.json`](../morphogenesis/experiments/L1_field/e6p_survfd_s176.json) | other | 18445 | `2b3f3732cd8551a7f91e023b55d162cc18087818721c2b86de023d0547d7a539` |
| [`morphogenesis/experiments/L1_field/e6p_survfd_s177.json`](../morphogenesis/experiments/L1_field/e6p_survfd_s177.json) | other | 11524 | `3c2d83be10d47df40481ebccb39ddaf5112286805edfd9777e3f80156cff079e` |
| [`morphogenesis/experiments/L1_field/e6p_survfd_s178.json`](../morphogenesis/experiments/L1_field/e6p_survfd_s178.json) | other | 16960 | `69464fed5226c9d92db5f7236fbd369c8a9f0bf465f7ba87169e213c6185b8a7` |
| [`morphogenesis/experiments/L1_field/e6p_survfd_s179.json`](../morphogenesis/experiments/L1_field/e6p_survfd_s179.json) | other | 10928 | `0d9a9a55995391d5ffaebaf9882343608b6d0c7623f548975195e6525d49f0a7` |
| [`morphogenesis/experiments/L1_field/e6p_survfd_s180.json`](../morphogenesis/experiments/L1_field/e6p_survfd_s180.json) | other | 13771 | `921b4805b00ecc63601b83ada724bb5b392d1901283d950ed7ba73d12798ee79` |
| [`morphogenesis/experiments/L1_field/e6q_ctrl_h_s171.json`](../morphogenesis/experiments/L1_field/e6q_ctrl_h_s171.json) | other | 9471 | `d081e39ea00dff545f61b41a4ce4360c72799bad7324a02d98356635586b63c8` |
| [`morphogenesis/experiments/L1_field/e6q_ctrl_h_s172.json`](../morphogenesis/experiments/L1_field/e6q_ctrl_h_s172.json) | other | 9461 | `baaa9d36543f354253b56c64da83927c44e4c41617f8bf547a3483ec55b0e3c3` |
| [`morphogenesis/experiments/L1_field/e6q_ctrl_h_s173.json`](../morphogenesis/experiments/L1_field/e6q_ctrl_h_s173.json) | other | 9471 | `a48992d388ea8555d9951c8b96d66df0ad42266ff92237dbdf8ad405aea8ec82` |
| [`morphogenesis/experiments/L1_field/e6q_ctrl_h_s174.json`](../morphogenesis/experiments/L1_field/e6q_ctrl_h_s174.json) | other | 9471 | `752559070b060863a78ea19ec17aa0011be564cfc713dd1feb719bbc885dd846` |
| [`morphogenesis/experiments/L1_field/e6q_ctrl_h_s175.json`](../morphogenesis/experiments/L1_field/e6q_ctrl_h_s175.json) | other | 9469 | `4fc891be7ea8ed3de076009fc125f5dcdd31f658673bda8bf874625f0ac25f00` |
| [`morphogenesis/experiments/L1_field/e6q_ctrl_h_s176.json`](../morphogenesis/experiments/L1_field/e6q_ctrl_h_s176.json) | other | 9471 | `55b7db155e4899084e18c7936c99bacba93a852643742c46cca78abbfba31bd6` |
| [`morphogenesis/experiments/L1_field/e6q_ctrl_h_s177.json`](../morphogenesis/experiments/L1_field/e6q_ctrl_h_s177.json) | other | 9470 | `fac7086754c09f9c02edba20e48ae62024395d8877313e67b16acc2b3a6fd4ef` |
| [`morphogenesis/experiments/L1_field/e6q_ctrl_h_s178.json`](../morphogenesis/experiments/L1_field/e6q_ctrl_h_s178.json) | other | 9469 | `864a1d4b7fb24115d187920267ad4a8d88b7e5e031fbad295c5f4a18b04fb336` |
| [`morphogenesis/experiments/L1_field/e6q_ctrl_h_s179.json`](../morphogenesis/experiments/L1_field/e6q_ctrl_h_s179.json) | other | 9467 | `a77855521607000ce3c7598e939d8f087021ad778e558a51e27f4aeaca572df8` |
| [`morphogenesis/experiments/L1_field/e6q_ctrl_h_s180.json`](../morphogenesis/experiments/L1_field/e6q_ctrl_h_s180.json) | other | 9466 | `f2f6a7c6b58c7d8395e2984a8253136f1547e972a88493540adabc956ac7196b` |
| [`morphogenesis/experiments/L1_field/e6q_series_index.json`](../morphogenesis/experiments/L1_field/e6q_series_index.json) | other | 2449 | `48ff226b47108337769155d956b616a36de7210801b7a3fb532142f3de83db52` |
| [`morphogenesis/experiments/L1_field/e6q_survfd_h_s171.json`](../morphogenesis/experiments/L1_field/e6q_survfd_h_s171.json) | other | 8766 | `fa46263c4c064064c6b06f06617dc72117d2797e5486d52bff93ab4014df11f5` |
| [`morphogenesis/experiments/L1_field/e6q_survfd_h_s172.json`](../morphogenesis/experiments/L1_field/e6q_survfd_h_s172.json) | other | 8908 | `1017420c1ed723f479973f646e1cd821c168d6d76748e8843f20fd53196ecc4c` |
| [`morphogenesis/experiments/L1_field/e6q_survfd_h_s173.json`](../morphogenesis/experiments/L1_field/e6q_survfd_h_s173.json) | other | 7896 | `32ea1aaebd03f469eb7243dfef7f4d412b3427b177cf8ad797647c97187b518e` |
| [`morphogenesis/experiments/L1_field/e6q_survfd_h_s174.json`](../morphogenesis/experiments/L1_field/e6q_survfd_h_s174.json) | other | 10050 | `54982d29ef976d13470750fd48acc28ae602fd32587f41f36e1bda76c9640043` |
| [`morphogenesis/experiments/L1_field/e6q_survfd_h_s175.json`](../morphogenesis/experiments/L1_field/e6q_survfd_h_s175.json) | other | 8036 | `9eab5ba2d4c886a144336653352e1f2878776ef74add5a49761f2c912340e909` |
| [`morphogenesis/experiments/L1_field/e6q_survfd_h_s176.json`](../morphogenesis/experiments/L1_field/e6q_survfd_h_s176.json) | other | 10021 | `fae363fbf3d679e030f3d085c8578f53927e04b79a3664d1d8cb0b2d13006832` |
| [`morphogenesis/experiments/L1_field/e6q_survfd_h_s177.json`](../morphogenesis/experiments/L1_field/e6q_survfd_h_s177.json) | other | 8193 | `10d13376084efd4e97aa9f2197d3ff9a3bd5a4351756ab1f6393357884fc3a8d` |
| [`morphogenesis/experiments/L1_field/e6q_survfd_h_s178.json`](../morphogenesis/experiments/L1_field/e6q_survfd_h_s178.json) | other | 10924 | `504cf6305c086501564f80f18c0d8ac1dd311df62c4a7655ff31abbf34c51a37` |
| [`morphogenesis/experiments/L1_field/e6q_survfd_h_s179.json`](../morphogenesis/experiments/L1_field/e6q_survfd_h_s179.json) | other | 8631 | `3dc163fae3e643404224fd61cf25db7cced1525c3101183b8403d1bea1232d7d` |
| [`morphogenesis/experiments/L1_field/e6q_survfd_h_s180.json`](../morphogenesis/experiments/L1_field/e6q_survfd_h_s180.json) | other | 8048 | `8cb69381d04db0ee86443f7b82cc9c8e94d9c9cc2da6c513e2dabb70be7c594c` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s171.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s171.json) | other | 4209 | `bda83d07b1395a6377a6f2a3d851ece40ca1395ce5580c12b65cb76c180adb49` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s172.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s172.json) | other | 4229 | `4ac9700aa78b7740753c07e403fc4f8b5bca138de571c93bcc66e47bf04ddd14` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s173.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s173.json) | other | 4131 | `5d9fcc0519d33531ffcdf3e9f7c05440d05b141c06a433818691480b82ab1b44` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s174.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s174.json) | other | 4320 | `2bad530fc9f6b58b09b6af01c1b1babeab262d27122c185942a0361df8836366` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s175.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s175.json) | other | 4135 | `da21d2ac607caf32c43589942e7bd884f649460c063c4d05862c1ecfa5a86525` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s176.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s176.json) | other | 4290 | `e6ed7dc7a65779981277735b388e109bef6941b16471696d2fc7025c0d3dd6c2` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s177.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s177.json) | other | 4159 | `88a1e45f6c64d09eaf78be1ab7befbf698d4b750b6ba1024cf58bf9d35f9fc0f` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s178.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s178.json) | other | 4407 | `97bcaaa5e2d6303c5d4c4389846b28154372917690c6eef038a49798b726fdf4` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s179.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s179.json) | other | 4208 | `ed68c4f81889d602f23192b8fabd3bf174daac81f2e6c9f6610bf0ad936a0597` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s180.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_homog_s180.json) | other | 4155 | `ba7162e3e39dea6a54160d44ae6b81812c70a009f6da65896315fc88504bff27` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_static_s171.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_static_s171.json) | other | 4224 | `92f7e70b0e86942f806e06cfc3ad937d940284cfc9353fa8f0d6d7ac0d4765c9` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_static_s172.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_static_s172.json) | other | 4311 | `af8285009574158e3b47544067136046c78e83e8bc57ef3af608dc5a7eaf91ea` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_static_s173.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_static_s173.json) | other | 4668 | `b9431762bdad27e1b00947b2492159c71fb3c673113418536cdd68f4524c9fd1` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_static_s174.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_static_s174.json) | other | 4437 | `b4f1154b3cbb9af572798c54ccebaf1a2a9ccfcc38afa53a58c9d30864df54f7` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_static_s175.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_static_s175.json) | other | 4235 | `3f942734bcd929325304e28de51968c27665ae95617ed9efa1163ca9bcf7ff8e` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_static_s176.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_static_s176.json) | other | 4340 | `2f407d1ba2d20831e32bd8a09c3b4ff109028b7393014640e85e48303da9ccb1` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_static_s177.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_static_s177.json) | other | 4418 | `c37e89eaef6bee93eacbfe9197290987db795cc7e68d06ba1654ea887b77c16e` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_static_s178.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_static_s178.json) | other | 4397 | `7da04a15e9ad7043d5b5c9a0db5ddb0ed01af3f0f6a1f77abf1b0760c2855afe` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_static_s179.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_static_s179.json) | other | 4560 | `9f5112171c5a82a63b67f0d5c3f1cc7d19d17543cf4a952d8144f07846567ae8` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.2_static_s180.json`](../morphogenesis/experiments/L1_field/hl1_amp0.2_static_s180.json) | other | 4299 | `7657594cb68098a1f29893493279c9a6170c53fd66a89ea4cbdadee0834edf02` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s171.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s171.json) | other | 4355 | `2ec70e91ebcee22151bb6cbc3e9c66cbcafa02a9e0f413e382fab81667187e87` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s172.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s172.json) | other | 4375 | `60903d53df05060a285f702e5b019a50b9e5a69e2f592649bbbd5103cf81c98d` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s173.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s173.json) | other | 4277 | `399e3b9ae6034478b114db90efd71ef8f9c1ffb0cbfe22df711032430650783f` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s174.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s174.json) | other | 4466 | `54c331479ab83c7fe07a06140ab7f680b6fbfed93d13cd992b3c5cb146732263` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s175.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s175.json) | other | 4281 | `c2bc421295f00a7efd36fc0f7fc8b2d7160049a25bc2d3d43d68c99705a2a328` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s176.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s176.json) | other | 4436 | `c178ad5ca5eeee26c573e0f0c8c82cb245427a7870ead6ef0bd8da3c6037a276` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s177.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s177.json) | other | 4305 | `31b5bd08be06bd1dbb8247f0f2fa94d5304a0f432d0ef64d643f0a6c73a14c6f` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s178.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s178.json) | other | 4553 | `c7055b06c657a8831fb4922a74fe455be555a4be9114594f89f93683b6f373c3` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s179.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s179.json) | other | 4354 | `22b49f1120ac4056638153206f0c8d8639155ae1bf2f10e5abbf3ecc45d29aa9` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s180.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_homog_s180.json) | other | 4301 | `40a59f68208c65cc9f2cf5f6c77624ede4108a973f8869344da348c61b852874` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_static_s171.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_static_s171.json) | other | 4527 | `eeb54ca3762f3199f9ee2de0af8b17c2e0f13bb9610cb8bd61e969d101151586` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_static_s172.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_static_s172.json) | other | 4173 | `b5240e51042deab3d67d62ec6ef4b9a86b80488b99a5520194bc9acb0a1d2af3` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_static_s173.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_static_s173.json) | other | 4593 | `77f7a96ff7b992ddfc4ad897522d6e9c0e778a77455db338450e6dd5584e065e` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_static_s174.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_static_s174.json) | other | 4598 | `2a44d935f995f4f4371ee4a284037757570e08fb8fbfddc033943eb1fe734914` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_static_s175.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_static_s175.json) | other | 5023 | `a1ba51db31d7cbaaae9bce52495ab184a3be7436e9ae5cc2d140b0f33c069594` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_static_s176.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_static_s176.json) | other | 4693 | `1ebf39f4b57cd515cee1e0a4c55089aec347147e33c7ce9f763123a6392e4186` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_static_s177.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_static_s177.json) | other | 4726 | `be5ddff4b55341fdf4382faad4084021f925cce6b2c34179900fdc14e449dd44` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_static_s178.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_static_s178.json) | other | 4521 | `dbe599a033bb31f5ae78a2a762e822cf1e92a836c7582ed36dea40952ce8f2a0` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_static_s179.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_static_s179.json) | other | 4687 | `b0e475ab79af1245e7df9a1c3930aa3a31c438916fdbd79bc2d87a8202cc83ff` |
| [`morphogenesis/experiments/L1_field/hl1_amp0.8_static_s180.json`](../morphogenesis/experiments/L1_field/hl1_amp0.8_static_s180.json) | other | 4500 | `80b2fce2c9e62be700dc5f9cb6595f0380aece73345c33b2e87fcb28ba2e3d2c` |
| [`morphogenesis/experiments/L1_field/l1_field_matrix.json`](../morphogenesis/experiments/L1_field/l1_field_matrix.json) | other | 54515 | `eeb7a172438adc848c6eed01f4d1d6fb53461ef46ac3c01b38aa9f1a7754e9fe` |
| [`morphogenesis/experiments/L1_field/lifetimes_matrix.json`](../morphogenesis/experiments/L1_field/lifetimes_matrix.json) | other | 3148 | `3dee1f57606fb08b3fd6685ce79e8b7508f2502d14d42d21cb20d8517d1cb7c5` |
| [`morphogenesis/experiments/L1_field/n20_p300_s171.json`](../morphogenesis/experiments/L1_field/n20_p300_s171.json) | other | 4482 | `74895da811290b4ef2b731b5a7237cbaf39757a43c8151f80829023dfa5f3e6d` |
| [`morphogenesis/experiments/L1_field/n20_p300_s172.json`](../morphogenesis/experiments/L1_field/n20_p300_s172.json) | other | 4390 | `4aa9d0dc47ed8a48477d3925a394e040e2096cf286a01bb30e48d3b4c074397c` |
| [`morphogenesis/experiments/L1_field/n20_p300_s173.json`](../morphogenesis/experiments/L1_field/n20_p300_s173.json) | other | 4790 | `2cd264a55e480c5336d896cc97a7810c089326edf3085b4373417d9ecbdbf85b` |
| [`morphogenesis/experiments/L1_field/n20_p300_s174.json`](../morphogenesis/experiments/L1_field/n20_p300_s174.json) | other | 4850 | `9795742a44f6ed0d6d46bf12b8f2254c4b99c26a25ad29bb33051b9d38789468` |
| [`morphogenesis/experiments/L1_field/n20_p300_s175.json`](../morphogenesis/experiments/L1_field/n20_p300_s175.json) | other | 4351 | `ab9c309faffc8ebf3d828f9a73538b86d6a47accf7a54f6af88380a34be56f84` |
| [`morphogenesis/experiments/L1_field/n20_p300_s176.json`](../morphogenesis/experiments/L1_field/n20_p300_s176.json) | other | 4383 | `9adac5db4472c97b584f134a4530963cba5d3842974a1b4ea7364df6bb410fd6` |
| [`morphogenesis/experiments/L1_field/n20_p300_s177.json`](../morphogenesis/experiments/L1_field/n20_p300_s177.json) | other | 4504 | `f51d4083bc32d101c6e92cacb1d21d7a1ce4107c83db3df9c4774fc51734f7a6` |
| [`morphogenesis/experiments/L1_field/n20_p300_s178.json`](../morphogenesis/experiments/L1_field/n20_p300_s178.json) | other | 4545 | `a7ec2e31abcf0247282a113e15d7b4ca9354bdf613e95a66b92f66d0ceb7a2ac` |
| [`morphogenesis/experiments/L1_field/n20_p300_s179.json`](../morphogenesis/experiments/L1_field/n20_p300_s179.json) | other | 4362 | `d4c407b76fa08b753015735a70bae75bd498b0305da6c0390904d21604483d05` |
| [`morphogenesis/experiments/L1_field/n20_p300_s180.json`](../morphogenesis/experiments/L1_field/n20_p300_s180.json) | other | 4642 | `6a2b14373fadfb0c4b449bb27b2a37e6840b8ead080185bdd3b0a9cbc062388b` |
| [`morphogenesis/experiments/L1_field/n20_p300_s181.json`](../morphogenesis/experiments/L1_field/n20_p300_s181.json) | other | 4251 | `4db6531aa0b9e55b09ae124bc9d9032835b0db65e455a87651d4892c3fa34f97` |
| [`morphogenesis/experiments/L1_field/n20_p300_s182.json`](../morphogenesis/experiments/L1_field/n20_p300_s182.json) | other | 4614 | `c4fa9bef99523e574b87734d37c1415d7ab391557a883e42f9f2dcd1fd1ab984` |
| [`morphogenesis/experiments/L1_field/n20_p300_s183.json`](../morphogenesis/experiments/L1_field/n20_p300_s183.json) | other | 4775 | `a6f0e67a8df1fc30ca070527dac14264111043d6a71edc6971bf62134ca4ff79` |
| [`morphogenesis/experiments/L1_field/n20_p300_s184.json`](../morphogenesis/experiments/L1_field/n20_p300_s184.json) | other | 4279 | `b3547f2f464c4a865f7bebfbf169fd6d8523b7cc3edb3242df525248f79e0deb` |
| [`morphogenesis/experiments/L1_field/n20_p300_s185.json`](../morphogenesis/experiments/L1_field/n20_p300_s185.json) | other | 4796 | `404eee509fb705e8630ea365598f4fff1ffa839d5500590e38375b622d1ee6c9` |
| [`morphogenesis/experiments/L1_field/n20_p300_s186.json`](../morphogenesis/experiments/L1_field/n20_p300_s186.json) | other | 4343 | `4a152d29e8521104fe50ffb24de9d91fa09ba585d21793f181a013a75a96e6f9` |
| [`morphogenesis/experiments/L1_field/n20_p300_s187.json`](../morphogenesis/experiments/L1_field/n20_p300_s187.json) | other | 4272 | `f972b030f90e16594a2ac0e564e45f4e6e7d896f88b895c9e8334f2cefecbb7c` |
| [`morphogenesis/experiments/L1_field/n20_p300_s188.json`](../morphogenesis/experiments/L1_field/n20_p300_s188.json) | other | 4493 | `ab2da10d81a58458c14764c7d4cef4ca4f276b32cb915d7ea36cebf53eba7028` |
| [`morphogenesis/experiments/L1_field/n20_p300_s189.json`](../morphogenesis/experiments/L1_field/n20_p300_s189.json) | other | 4332 | `016a7638d3607e40f1cbdb5c0fa41a7f8a0a053eed9d104f7e93dc99a380aad8` |
| [`morphogenesis/experiments/L1_field/n20_p300_s190.json`](../morphogenesis/experiments/L1_field/n20_p300_s190.json) | other | 4537 | `11c607f07ac00f25cf67f92102127b5c70969702a35d89f8bfdfc4d8e6f97f37` |
| [`morphogenesis/experiments/L1_field/n20_static_s171.json`](../morphogenesis/experiments/L1_field/n20_static_s171.json) | other | 4769 | `2d77bfd740b3800b572a05df4ebd79054a5168e7da60e18724ed381d92dd892b` |
| [`morphogenesis/experiments/L1_field/n20_static_s172.json`](../morphogenesis/experiments/L1_field/n20_static_s172.json) | other | 5393 | `4d663687f2afa0753d61d2e6d2fafc6bdd2097ac9cd636df5ae40c78200908fc` |
| [`morphogenesis/experiments/L1_field/n20_static_s173.json`](../morphogenesis/experiments/L1_field/n20_static_s173.json) | other | 4473 | `b199b14ade2a5e5f34c7f93ac4e58caa59cad641e3a023f7cc9ab41f1102654e` |
| [`morphogenesis/experiments/L1_field/n20_static_s174.json`](../morphogenesis/experiments/L1_field/n20_static_s174.json) | other | 4415 | `1e73222779edfe68d5d74f6a66d82610cd3585a1175217a0e757022e8a04bc5c` |
| [`morphogenesis/experiments/L1_field/n20_static_s175.json`](../morphogenesis/experiments/L1_field/n20_static_s175.json) | other | 4377 | `bb9e9e0f634f152843543cf8700131b2258b81edff10bfedd209f272f8083f75` |
| [`morphogenesis/experiments/L1_field/n20_static_s176.json`](../morphogenesis/experiments/L1_field/n20_static_s176.json) | other | 5027 | `356797f716d1375e671552a502c3f55c8a14b40b0ae9d45b37ad82dfcc9e619a` |
| [`morphogenesis/experiments/L1_field/n20_static_s177.json`](../morphogenesis/experiments/L1_field/n20_static_s177.json) | other | 4488 | `50eafc863d00cef485007746a9c54c2b8dcb2bb1eb252073aa9a4a709597df30` |
| [`morphogenesis/experiments/L1_field/n20_static_s178.json`](../morphogenesis/experiments/L1_field/n20_static_s178.json) | other | 4856 | `0bfc1f563a875d2072e0dd7de8c4e1bac065a5ca61b283944dd976f29f5aeb5d` |
| [`morphogenesis/experiments/L1_field/n20_static_s179.json`](../morphogenesis/experiments/L1_field/n20_static_s179.json) | other | 4398 | `984a68858cc11d4533a57068e3cf9aa6cbc50297bd4265fff196b9c60cd4bbe0` |
| [`morphogenesis/experiments/L1_field/n20_static_s180.json`](../morphogenesis/experiments/L1_field/n20_static_s180.json) | other | 4632 | `6227ba5ec997acde5b61a3f2587434fc1527c0f6d9f2c3118f565fa8ef8bffec` |
| [`morphogenesis/experiments/L1_field/n20_static_s181.json`](../morphogenesis/experiments/L1_field/n20_static_s181.json) | other | 4458 | `b2947f2bec9f8d615ecefefe7931df7be52d1d9307d9fd8d4b6c5be7cc3330c6` |
| [`morphogenesis/experiments/L1_field/n20_static_s182.json`](../morphogenesis/experiments/L1_field/n20_static_s182.json) | other | 4308 | `51ef6aec707a9642291cc6882bf97bc0d7e2b20c3a08abdd55814020c31fa022` |
| [`morphogenesis/experiments/L1_field/n20_static_s183.json`](../morphogenesis/experiments/L1_field/n20_static_s183.json) | other | 4346 | `e97f308c75e0b54c381d9d9c8a5a19ac66e5ab67e9f5176b37739ade20589128` |
| [`morphogenesis/experiments/L1_field/n20_static_s184.json`](../morphogenesis/experiments/L1_field/n20_static_s184.json) | other | 4593 | `05da9d0a9188f66e97b4c341ab5d2936624c55d3381d45fb36b5e9b57d0889dc` |
| [`morphogenesis/experiments/L1_field/n20_static_s185.json`](../morphogenesis/experiments/L1_field/n20_static_s185.json) | other | 5762 | `b538be0274837687cf9e92555e7deb29c49cb779940bc0e92dca914014c5c0e5` |
| [`morphogenesis/experiments/L1_field/n20_static_s186.json`](../morphogenesis/experiments/L1_field/n20_static_s186.json) | other | 4798 | `7a70989fc6403882b88f5a90207935f2e35979a911f6d569550bd5945f490068` |
| [`morphogenesis/experiments/L1_field/n20_static_s187.json`](../morphogenesis/experiments/L1_field/n20_static_s187.json) | other | 4692 | `9ef5400fb10614f6e695afe4827bf77f5db6a44fa5e97e310552e2a5a6b41783` |
| [`morphogenesis/experiments/L1_field/n20_static_s188.json`](../morphogenesis/experiments/L1_field/n20_static_s188.json) | other | 4490 | `6dc906ed6a9f9b8b58d566be428c5123242746214bd91ae9bab75014ea65a3a0` |
| [`morphogenesis/experiments/L1_field/n20_static_s189.json`](../morphogenesis/experiments/L1_field/n20_static_s189.json) | other | 4339 | `921a81f4fe7e8072e730676649dc2430e2a50a093efcb785138cb3a3ffa18eaa` |
| [`morphogenesis/experiments/L1_field/n20_static_s190.json`](../morphogenesis/experiments/L1_field/n20_static_s190.json) | other | 5007 | `db3928a5c447f410467c907af3f916df90270bd8c8379489e9caa8c9d6a0dbcc` |
| [`morphogenesis/experiments/L1_field/te_anticipation.json`](../morphogenesis/experiments/L1_field/te_anticipation.json) | other | 2559 | `b02fc9236fe8b9cdecaf20f54e8a9f7f77e0a8bda9efaa32b9b981abd23c6b33` |
| [`morphogenesis/experiments/L1_field/x100_f030_s291.json`](../morphogenesis/experiments/L1_field/x100_f030_s291.json) | other | 962248 | `ff8235cb36aff13076f6d69812e7c9a38e41a3be498f7351fc086a98357e3ee7` |
| [`morphogenesis/experiments/L1_field/x100_f030_s292.json`](../morphogenesis/experiments/L1_field/x100_f030_s292.json) | other | 904554 | `3d0d5ff497f23ef81208db7fe47076269074c8a8663dec6b5d5adae3674c60f5` |
| [`morphogenesis/experiments/L1_field/x100_f030_s293.json`](../morphogenesis/experiments/L1_field/x100_f030_s293.json) | other | 924772 | `e16433fa9d65e24dbdfad8aa71c17679772a2afa9911b4740c5b79f71d946407` |
| [`morphogenesis/experiments/L1_field/x100_f030_s294.json`](../morphogenesis/experiments/L1_field/x100_f030_s294.json) | other | 964639 | `d4846d977ca82b200597c8e8dddc4e238010cca5759bf142aa181cef2d7ee2eb` |
| [`morphogenesis/experiments/L1_field/x100_f030_s295.json`](../morphogenesis/experiments/L1_field/x100_f030_s295.json) | other | 899450 | `90e08c5d4c314f0d1960d32502ffb24f2e62a076c0228d2b790ba1d571a6d646` |
| [`morphogenesis/experiments/L1_field/x100_f030_s296.json`](../morphogenesis/experiments/L1_field/x100_f030_s296.json) | other | 943357 | `af9c1d47a9fd2b54dd081fa604778884007cf6677ee13eb7410635262e5f8d07` |
| [`morphogenesis/experiments/L1_field/x100_f030_s297.json`](../morphogenesis/experiments/L1_field/x100_f030_s297.json) | other | 898894 | `d1388fefe07a0161541ce258e5a5c6c51911f67b9cbc869b0fbc68a1c91c4a8f` |
| [`morphogenesis/experiments/L1_field/x100_f030_s298.json`](../morphogenesis/experiments/L1_field/x100_f030_s298.json) | other | 904411 | `a51bf324b85891ac6507594704c6d199ec661550a4d4a254b28f33050792de56` |
| [`morphogenesis/experiments/L1_field/x100_f030_s299.json`](../morphogenesis/experiments/L1_field/x100_f030_s299.json) | other | 900320 | `05ff91faddfac7cd5ad90fce744f16d00fc59da70a504bb591475defc4fd363a` |
| [`morphogenesis/experiments/L1_field/x100_f030_s300.json`](../morphogenesis/experiments/L1_field/x100_f030_s300.json) | other | 1001995 | `314455c2fe87dcc8ffd2f0d96dadc0a9c7127cd58f2d043086d52514e6ca9f31` |
| [`morphogenesis/experiments/L1_field/x100_f040_s291.json`](../morphogenesis/experiments/L1_field/x100_f040_s291.json) | other | 252063 | `2f553db318c0e9fd5528bcb07492229a4a300aa5c765bd391007d9431e3e0a15` |
| [`morphogenesis/experiments/L1_field/x100_f040_s292.json`](../morphogenesis/experiments/L1_field/x100_f040_s292.json) | other | 319034 | `11c7b06ace33b89c7508737764c0b219c148db72db74b6af56750e3c3d105708` |
| [`morphogenesis/experiments/L1_field/x100_f040_s293.json`](../morphogenesis/experiments/L1_field/x100_f040_s293.json) | other | 240823 | `5c5525530b5674ca2b0b2cf1e8fc1ae7e808b661c7b66fb90a4c507f895e47bf` |
| [`morphogenesis/experiments/L1_field/x100_f040_s294.json`](../morphogenesis/experiments/L1_field/x100_f040_s294.json) | other | 233862 | `028f59e07378e12a180a2c7815fff88496f11c5fd74e979f487fb35ed25c63d3` |
| [`morphogenesis/experiments/L1_field/x100_f040_s295.json`](../morphogenesis/experiments/L1_field/x100_f040_s295.json) | other | 212818 | `797993f31633dfa6547eeebf50b443ab606c2f4fb09a9c9e1d0c03e90a1180a8` |
| [`morphogenesis/experiments/L1_field/x100_f040_s296.json`](../morphogenesis/experiments/L1_field/x100_f040_s296.json) | other | 220188 | `2305305dc6a688718fa8a7654f53505be1cfb469d88bb59131eeea582f5d11ff` |
| [`morphogenesis/experiments/L1_field/x100_f040_s297.json`](../morphogenesis/experiments/L1_field/x100_f040_s297.json) | other | 212755 | `ee52047439ab4a6630ec6b9d80038b58e5c9e59406e763b81163e0f5d189d5e1` |
| [`morphogenesis/experiments/L1_field/x100_f040_s298.json`](../morphogenesis/experiments/L1_field/x100_f040_s298.json) | other | 200689 | `060027a5a0cb83d77c9534436319547f0cdc4b02d795f493a1768df90594cc22` |
| [`morphogenesis/experiments/L1_field/x100_f040_s299.json`](../morphogenesis/experiments/L1_field/x100_f040_s299.json) | other | 220279 | `bb6f8373c205c74c62bfde2ffb740f92cf8eae5c2e69933485b83e664d77433f` |
| [`morphogenesis/experiments/L1_field/x100_f040_s300.json`](../morphogenesis/experiments/L1_field/x100_f040_s300.json) | other | 308272 | `00dfadb68beda0b5fb9d3e2f1fed15b05e7fe2fdd0d9614e147ca951452f1c8b` |
| [`morphogenesis/experiments/L1_field/x100_series_index.json`](../morphogenesis/experiments/L1_field/x100_series_index.json) | other | 2020 | `2485532fea28fe3b7f4c8ec654457f7d888f724ad14530e2d71942158ad7e866` |
| [`morphogenesis/experiments/L1_field/x105_f030_s301.compact.json`](../morphogenesis/experiments/L1_field/x105_f030_s301.compact.json) | other | 443760 | `959e6ac4fa09c7bba37eae4a580fc9dadafae1a64c7cd51a94a39d819604fafa` |
| [`morphogenesis/experiments/L1_field/x105_f030_s302.compact.json`](../morphogenesis/experiments/L1_field/x105_f030_s302.compact.json) | other | 527032 | `4aca6a66f6b39d7f724a208ee80f63823d236ce6701d7897765e7f5f879f2ef8` |
| [`morphogenesis/experiments/L1_field/x105_f030_s303.compact.json`](../morphogenesis/experiments/L1_field/x105_f030_s303.compact.json) | other | 470474 | `bd8b6a45e0e3c6663457118a8f3da8036dd220b82d780a587aad1035d8bd6bb1` |
| [`morphogenesis/experiments/L1_field/x105_f030_s304.compact.json`](../morphogenesis/experiments/L1_field/x105_f030_s304.compact.json) | other | 514471 | `efb29ca081251d0a6922aadc6772476a251ba646a9bf2aa7cf5e1607b942c8ee` |
| [`morphogenesis/experiments/L1_field/x105_f030_s305.compact.json`](../morphogenesis/experiments/L1_field/x105_f030_s305.compact.json) | other | 511800 | `2e39715302d6ec9618e5d568934996a4cf07f4116eafabf905b439c36e826696` |
| [`morphogenesis/experiments/L1_field/x105_f030_s306.compact.json`](../morphogenesis/experiments/L1_field/x105_f030_s306.compact.json) | other | 553966 | `48ba8352db96f772563f04344e0c5d02fcfbc85aac5cb0818400bd4695ac763c` |
| [`morphogenesis/experiments/L1_field/x105_f030_s307.compact.json`](../morphogenesis/experiments/L1_field/x105_f030_s307.compact.json) | other | 551602 | `39a4c0865097cbc4b82b3749ceb0ca25c7e7edaa05071f4e737105d8002b836e` |
| [`morphogenesis/experiments/L1_field/x105_f030_s308.compact.json`](../morphogenesis/experiments/L1_field/x105_f030_s308.compact.json) | other | 560628 | `fbfe0f3bddf1e9531db93fba8f1fba7f4c67a57df113749b12e8cdcd759d4a0b` |
| [`morphogenesis/experiments/L1_field/x105_f030_s309.compact.json`](../morphogenesis/experiments/L1_field/x105_f030_s309.compact.json) | other | 520849 | `5a04cb441164e609bc88bd0e593bdd5da4a7fbe15dfef4b1cad8aea19853399f` |
| [`morphogenesis/experiments/L1_field/x105_f030_s310.compact.json`](../morphogenesis/experiments/L1_field/x105_f030_s310.compact.json) | other | 520615 | `150903ddda065995d3471903c9cb098ee1d24816fe54d4af353428580f9b1b77` |
| [`morphogenesis/experiments/L1_field/x105_f040_s301.compact.json`](../morphogenesis/experiments/L1_field/x105_f040_s301.compact.json) | other | 109505 | `ec92508e1a0c31d5f6b2fff43651d717ea5ebfe04d9ee5eda354ca98d6049b16` |
| [`morphogenesis/experiments/L1_field/x105_f040_s302.compact.json`](../morphogenesis/experiments/L1_field/x105_f040_s302.compact.json) | other | 85809 | `83a4c56de33ba3b7ab0b7f84f1ffcb56bda262291eaddb1501d12842a4245710` |
| [`morphogenesis/experiments/L1_field/x105_f040_s303.compact.json`](../morphogenesis/experiments/L1_field/x105_f040_s303.compact.json) | other | 103878 | `db3ed5860866cd93b5ea29e22989a60c4d1167e0d3bea5d4e6029ec242d11502` |
| [`morphogenesis/experiments/L1_field/x105_f040_s304.compact.json`](../morphogenesis/experiments/L1_field/x105_f040_s304.compact.json) | other | 117971 | `ae3afae27a0c0fd77b36062fce551689c0adcae6394f11ff1ad2002dc32ec236` |
| [`morphogenesis/experiments/L1_field/x105_f040_s305.compact.json`](../morphogenesis/experiments/L1_field/x105_f040_s305.compact.json) | other | 72765 | `60efaa68ed57e9d2f8c17c792db104b13e3df2942a117d56585d5518278bea44` |
| [`morphogenesis/experiments/L1_field/x105_f040_s306.compact.json`](../morphogenesis/experiments/L1_field/x105_f040_s306.compact.json) | other | 126001 | `59e5160e1ce94ff4676d4d0838e4773d9164053a2f149c5376bf207b883df486` |
| [`morphogenesis/experiments/L1_field/x105_f040_s307.compact.json`](../morphogenesis/experiments/L1_field/x105_f040_s307.compact.json) | other | 78755 | `cd4a0b0dcc41b577614b03ad43e83173af0205162deebb82ee2b4d54787d340e` |
| [`morphogenesis/experiments/L1_field/x105_f040_s308.compact.json`](../morphogenesis/experiments/L1_field/x105_f040_s308.compact.json) | other | 99181 | `cdb8afb18e680cafb07401552d7909e1ce8bf505e07cc5f418ac8a08c94bb05c` |
| [`morphogenesis/experiments/L1_field/x105_f040_s309.compact.json`](../morphogenesis/experiments/L1_field/x105_f040_s309.compact.json) | other | 86814 | `d0a58fb13d6ef478b84edd618669abaa0b8f9ee481aa3428fb51e2a08006008d` |
| [`morphogenesis/experiments/L1_field/x105_f040_s310.compact.json`](../morphogenesis/experiments/L1_field/x105_f040_s310.compact.json) | other | 99343 | `64dc4ed93cbfe1fb7eea37079654db334cc52cd9d7d6855525a7800473c6f462` |
| [`morphogenesis/experiments/L1_field/x108_f030_s301.compact.json`](../morphogenesis/experiments/L1_field/x108_f030_s301.compact.json) | other | 443760 | `e113f9b4d52a97e5ca3b99e0ce54c7b8effd7dbeb8b21f56c833792126d99e2c` |
| [`morphogenesis/experiments/L1_field/x108_f030_s302.compact.json`](../morphogenesis/experiments/L1_field/x108_f030_s302.compact.json) | other | 527032 | `b4c2bd163043a32f93c3d3710e41f087cec4d37c335b959f05c3a696f2ae7fc8` |
| [`morphogenesis/experiments/L1_field/x108_f030_s303.compact.json`](../morphogenesis/experiments/L1_field/x108_f030_s303.compact.json) | other | 470474 | `773c40cf0b5f8df50f840083258f3fe25eee34f90856564243033260e14bfad5` |
| [`morphogenesis/experiments/L1_field/x108_f030_s304.compact.json`](../morphogenesis/experiments/L1_field/x108_f030_s304.compact.json) | other | 514471 | `034b8be2080500aa1540ab42211733cefc531c63d28e8858a82ec1a9e398ad34` |
| [`morphogenesis/experiments/L1_field/x108_f030_s305.compact.json`](../morphogenesis/experiments/L1_field/x108_f030_s305.compact.json) | other | 511800 | `69b7bd7b722bc676228530c9098d9951ad2c3cb1abd59e35d2b9013fd37fdd6d` |
| [`morphogenesis/experiments/L1_field/x108_f030_s306.compact.json`](../morphogenesis/experiments/L1_field/x108_f030_s306.compact.json) | other | 553966 | `6b2ce475d6dc340232c1763ebe5c241f309bd4c7b14c926847a08843cd8cbb37` |
| [`morphogenesis/experiments/L1_field/x108_f030_s307.compact.json`](../morphogenesis/experiments/L1_field/x108_f030_s307.compact.json) | other | 551602 | `3845cbc935b0f24df90e271cb4eb2c9970379de1db3cf1c4dc52457853147af5` |
| [`morphogenesis/experiments/L1_field/x108_f030_s308.compact.json`](../morphogenesis/experiments/L1_field/x108_f030_s308.compact.json) | other | 560628 | `a849ed054b2eec9e16262642b8b91579f284aae5aad69d345d5825761488d512` |
| [`morphogenesis/experiments/L1_field/x108_f030_s309.compact.json`](../morphogenesis/experiments/L1_field/x108_f030_s309.compact.json) | other | 520849 | `958dbec41f049a7a96dc083ffad7b1a41c269e1e4c0ec8512ec095fd2d892691` |
| [`morphogenesis/experiments/L1_field/x108_f030_s310.compact.json`](../morphogenesis/experiments/L1_field/x108_f030_s310.compact.json) | other | 520615 | `6a37c08028ef9e694e71a9b08e0bed35bd9572b3c0c44ab258ab57b067773c97` |
| [`morphogenesis/experiments/L1_field/x108_f040_s301.compact.json`](../morphogenesis/experiments/L1_field/x108_f040_s301.compact.json) | other | 109505 | `e6e8f96d2144aaee191230241d2be4420a8a766f03bf1011e1cc038a1482b3da` |
| [`morphogenesis/experiments/L1_field/x108_f040_s302.compact.json`](../morphogenesis/experiments/L1_field/x108_f040_s302.compact.json) | other | 85809 | `566cbe16657b333c3839892dbc19543443a9974236f6acd28bce45735491aec8` |
| [`morphogenesis/experiments/L1_field/x108_f040_s303.compact.json`](../morphogenesis/experiments/L1_field/x108_f040_s303.compact.json) | other | 103878 | `7cca0fe7d983b99d8d6aa6af7f0209af3f13db4654c985933a80199817969e01` |
| [`morphogenesis/experiments/L1_field/x108_f040_s304.compact.json`](../morphogenesis/experiments/L1_field/x108_f040_s304.compact.json) | other | 117971 | `1e4995c42d30d1db53a9ac30d51d3c31eac7f09d2a6ac3395414a4a239baa514` |
| [`morphogenesis/experiments/L1_field/x108_f040_s305.compact.json`](../morphogenesis/experiments/L1_field/x108_f040_s305.compact.json) | other | 72765 | `6aefbc84796cda1afd72f3ab1543ae1927db998ff6617972ce156ad6289c2679` |
| [`morphogenesis/experiments/L1_field/x108_f040_s306.compact.json`](../morphogenesis/experiments/L1_field/x108_f040_s306.compact.json) | other | 126001 | `05ffcca9cc4b1bbd7d8348a1f360d6655dd5ba4d43fd535ddc97fc15274d2663` |
| [`morphogenesis/experiments/L1_field/x108_f040_s307.compact.json`](../morphogenesis/experiments/L1_field/x108_f040_s307.compact.json) | other | 78755 | `3ee57ab72483bf4ee4f598efbd502f5caf5dafce15722a3e05cd7238a7a0adac` |
| [`morphogenesis/experiments/L1_field/x108_f040_s308.compact.json`](../morphogenesis/experiments/L1_field/x108_f040_s308.compact.json) | other | 99181 | `d3855527ab74ee8c7d2f7c8929bc713c18cb04e756fe9b2ab9ce96943827679e` |
| [`morphogenesis/experiments/L1_field/x108_f040_s309.compact.json`](../morphogenesis/experiments/L1_field/x108_f040_s309.compact.json) | other | 86814 | `d6ff4c5efa56d2e02ea29bbf04df04443d3f827f98ac6ad8a75fc766525ce049` |
| [`morphogenesis/experiments/L1_field/x108_f040_s310.compact.json`](../morphogenesis/experiments/L1_field/x108_f040_s310.compact.json) | other | 99343 | `0d728ed9c6561e4db28891f97a7e7a2287c5105fa0bca603bbee3a66bd18153e` |
| [`morphogenesis/experiments/L1_field/x110_f030_g010_s421.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g010_s421.compact.json) | other | 65310 | `3a699a439c039d9b5f8d592a1eb0c4eb03529b8ac6d61ee98d516902e1b8177a` |
| [`morphogenesis/experiments/L1_field/x110_f030_g010_s422.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g010_s422.compact.json) | other | 34951 | `546971807a17e72531af44632a558180c66f1d0b721fc0bc1d2b0e80d8e4657c` |
| [`morphogenesis/experiments/L1_field/x110_f030_g010_s423.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g010_s423.compact.json) | other | 70744 | `014006c0d665b0060b52d9d38df09db749792658e7df4bb471096a967caf6ac2` |
| [`morphogenesis/experiments/L1_field/x110_f030_g015_s421.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g015_s421.compact.json) | other | 35221 | `3a99b1a16273cc8de6ce3f63e9a95099c50b34e236700b48d7607372c2b1733f` |
| [`morphogenesis/experiments/L1_field/x110_f030_g015_s422.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g015_s422.compact.json) | other | 62953 | `6e0e258651a4fda5d4e1cfdeeb388a23d3ee12ef0137a9cedb9887e80421fc85` |
| [`morphogenesis/experiments/L1_field/x110_f030_g015_s423.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g015_s423.compact.json) | other | 54987 | `e2cd3f6c48c7e7be8b22424a2132e542c720eb83e649e5f391994796860d26ee` |
| [`morphogenesis/experiments/L1_field/x110_f030_g020_s421.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g020_s421.compact.json) | other | 43612 | `8379ced3d204ab808d3242f071da45d281404da9ae6f2407722ee4cd1a14976e` |
| [`morphogenesis/experiments/L1_field/x110_f030_g020_s422.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g020_s422.compact.json) | other | 22694 | `026ab5cd254038cb3207be519b252d3c37458dac489f04593bd69ed147d242ed` |
| [`morphogenesis/experiments/L1_field/x110_f030_g020_s423.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g020_s423.compact.json) | other | 44244 | `66b017a0e5966ab6d79d886028fbf9a3c243f413eb4f1ee19ce4bdde3dce5d81` |
| [`morphogenesis/experiments/L1_field/x110_f030_g030_s421.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g030_s421.compact.json) | other | 20865 | `e0deda6be79c8592fbec9540c95063e324b39d94eac5e6b57bed681c98f8fb72` |
| [`morphogenesis/experiments/L1_field/x110_f030_g030_s422.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g030_s422.compact.json) | other | 27726 | `8fa1e651a289d74ee4651016fa72240711090e5d5b7d0be0559cb3bbae2f5bf7` |
| [`morphogenesis/experiments/L1_field/x110_f030_g030_s423.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g030_s423.compact.json) | other | 7298 | `1b196aea7c5e12c3f03bb80300265b7f9cc8bb3cf180a61b8d8d1eb1a57a40f4` |
| [`morphogenesis/experiments/L1_field/x110_f030_g050_s421.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g050_s421.compact.json) | other | 4222 | `810d1295380e315e33bc3a1c24cdc5f646b6be1ac16171fd960b4b937db23d8d` |
| [`morphogenesis/experiments/L1_field/x110_f030_g050_s422.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g050_s422.compact.json) | other | 4210 | `e519a9c05d326a4a6200b423554a8aa0cecfda14c83d8281c09be5e92d2d8434` |
| [`morphogenesis/experiments/L1_field/x110_f030_g050_s423.compact.json`](../morphogenesis/experiments/L1_field/x110_f030_g050_s423.compact.json) | other | 21587 | `ebab9e18237ab9d5601c55ccee07626aea7c3e8342b6403e07222f8a8c382965` |
| [`morphogenesis/experiments/L1_field/x110_f040_g010_s421.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g010_s421.compact.json) | other | 32498 | `5cae0a8823fca06d8e13901f636222ab2fed49f01ef7649eeca798267a73ab44` |
| [`morphogenesis/experiments/L1_field/x110_f040_g010_s422.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g010_s422.compact.json) | other | 35497 | `35d9a453a77d670670b8a1e4b1844cde7b360caf1ed15c9a862063def378cfa6` |
| [`morphogenesis/experiments/L1_field/x110_f040_g010_s423.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g010_s423.compact.json) | other | 18327 | `971f43b5800bc1da7fc00b3adb1c7fdffa1105c2f4a29d8efe1e7215d582f586` |
| [`morphogenesis/experiments/L1_field/x110_f040_g015_s421.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g015_s421.compact.json) | other | 6758 | `701db5d1120e9e634491689b48a4b9ee88abef19c8a913ecd4256aa58a6c2599` |
| [`morphogenesis/experiments/L1_field/x110_f040_g015_s422.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g015_s422.compact.json) | other | 6723 | `957af722928be83f76c382c5cd7735936524c61ccc6f5fac392aecfe4ec7d26e` |
| [`morphogenesis/experiments/L1_field/x110_f040_g015_s423.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g015_s423.compact.json) | other | 8650 | `31ff23946a8e1affa0490168bbcee4f736f07098309f9b39f02ea21c4ee2c7d3` |
| [`morphogenesis/experiments/L1_field/x110_f040_g020_s421.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g020_s421.compact.json) | other | 6817 | `919255c51e8a7ac3c598d93a47d1beebe0386ab98ab7dac14d808646925434a1` |
| [`morphogenesis/experiments/L1_field/x110_f040_g020_s422.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g020_s422.compact.json) | other | 6737 | `c52fdb2b7bfd9a60d2910df963597cec675f558de8e1b1d4e01826fca8ad36af` |
| [`morphogenesis/experiments/L1_field/x110_f040_g020_s423.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g020_s423.compact.json) | other | 6361 | `50a898480ccb810ca9f208941229764f0db9c2d27cd2ad77739dcebc9ad23293` |
| [`morphogenesis/experiments/L1_field/x110_f040_g030_s421.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g030_s421.compact.json) | other | 6721 | `9896f8a14f73a0519d06263741171cdd9f5a9e59274e2c5fdc38baffaef88cba` |
| [`morphogenesis/experiments/L1_field/x110_f040_g030_s422.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g030_s422.compact.json) | other | 6459 | `9acf29ead9f09647ea468e3570aefcfe42598902206e66c1cc1a001c010df58a` |
| [`morphogenesis/experiments/L1_field/x110_f040_g030_s423.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g030_s423.compact.json) | other | 4454 | `d6136296af327484566add9dbac2862689117d188fed04e9b3252517c30069e1` |
| [`morphogenesis/experiments/L1_field/x110_f040_g050_s421.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g050_s421.compact.json) | other | 6211 | `9f361c94fad55519ae23b043893eb0c24da6b3e0146541bbdcd2caf7d03da201` |
| [`morphogenesis/experiments/L1_field/x110_f040_g050_s422.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g050_s422.compact.json) | other | 6216 | `9565f277837db2766c203bf29b6b77b22bfbcefa109e253b6fdaced6be70fe33` |
| [`morphogenesis/experiments/L1_field/x110_f040_g050_s423.compact.json`](../morphogenesis/experiments/L1_field/x110_f040_g050_s423.compact.json) | other | 6165 | `7ba8bde9fe1f6e357eac1ab3d995026fd1ddc6d68094766e9b079bd822f3c0b9` |
| [`morphogenesis/experiments/L1_field/x110_series_index.json`](../morphogenesis/experiments/L1_field/x110_series_index.json) | other | 12897 | `29560eae0aa79f4c37a25cb4921943439bf89fae634b6eeb4006673191e98537` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr015_s301.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr015_s301.compact.json) | other | 87196 | `793adb0fb3f79840d2c618965fbacbf426ac457a0464ed9b6f887c59f988bb60` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr015_s302.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr015_s302.compact.json) | other | 102567 | `ee2c54d7f26c1cf08535fbd667582cf0cd087f567e3540034f2a533b81a64fdc` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr015_s303.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr015_s303.compact.json) | other | 86731 | `ca8c529ad91b27a104aedf359ad7a810aaedaef7024931e5a5a014aad324de9e` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr015_s304.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr015_s304.compact.json) | other | 102762 | `a876976eb920a871bbe9e96a7962724685e6ad0d14dbe601b9dbb15045f7bd77` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr015_s305.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr015_s305.compact.json) | other | 97830 | `a9447a2eed46a296090a526372bb768bb89034ed822a8b597aeab5bd3c1a3d7a` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr015_s306.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr015_s306.compact.json) | other | 108776 | `ebaf22a727b86e71b1015020dd44257893a8bd1920b7215916c3f5c3ca8c361a` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr015_s307.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr015_s307.compact.json) | other | 108183 | `8e33ac1dff3b660cce2ed0b00fa35fe3ceafa3786e690e6395abb53ba09a9719` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr015_s308.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr015_s308.compact.json) | other | 110929 | `b513e7f82d26c1af37b94f051591fe0040a9f344130fc78c3388b38879f70bdb` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr015_s309.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr015_s309.compact.json) | other | 102462 | `c529cf07c4e3c75e95ea9d9c5347a6dbf7fba410e01f94327f6464fa92453ca8` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr015_s310.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr015_s310.compact.json) | other | 99700 | `d0d9e50b48918bb741b702a1506ab209ea412d2d3df75e6df61294154011783b` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr025_s301.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr025_s301.compact.json) | other | 113889 | `380dbb421949a0ed52155773f1d1115131e86908de35bfe9fe8bd143395620a0` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr025_s302.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr025_s302.compact.json) | other | 123705 | `43270653f3fa1c0ecb48dd772a3604b0ac98a96d70329f1d19c698df217faa45` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr025_s303.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr025_s303.compact.json) | other | 122822 | `4334e52adc8ade6f123d21ee3c6cf4f4c7137a382a5a88c75ed21097cde0ecc2` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr025_s304.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr025_s304.compact.json) | other | 125194 | `6b431c8a2facb9dfdc2eed23ab88e6598276b5b54cd34f4889f4788f42b3210a` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr025_s305.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr025_s305.compact.json) | other | 129396 | `2774b7af534cd007c6deee32da8b9ce31a50dfe6f32579a6a1496cd4b36927e5` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr025_s306.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr025_s306.compact.json) | other | 122233 | `660cc2f28a3216b97adc82aaaa03821a8c4e3c5feb1eb01ef6060ac7df3c74a1` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr025_s307.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr025_s307.compact.json) | other | 127797 | `6734aa2d3ba998e06051636ec0ad2419bba04f09f67c86a10f84a6f3ae63b4da` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr025_s308.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr025_s308.compact.json) | other | 131991 | `6daf799953d4665211b9c1f38b0345a09517c28623be00dcf89e900da70eb5dc` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr025_s309.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr025_s309.compact.json) | other | 123331 | `a196113dbd8df17c9b63809c3048ef135ece008259214993a193066c2886722b` |
| [`morphogenesis/experiments/L1_field/x112b_f030_thr025_s310.compact.json`](../morphogenesis/experiments/L1_field/x112b_f030_thr025_s310.compact.json) | other | 128723 | `976ae6a19f5971aa7ee4e7e4606e97629e6bd7fc8aa072cf4d4ed76ec1f3db75` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr015_s301.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr015_s301.compact.json) | other | 12172 | `c4846dfec10fe5e022296bef08a7000b862af3e960886a24cc2ba622b98ef0ff` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr015_s302.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr015_s302.compact.json) | other | 8340 | `9c764bb2c9e6fa7656777ccbbd923e3656d62db9e605ad7c220fb2eb06bbb533` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr015_s303.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr015_s303.compact.json) | other | 9939 | `7bb1d0295ba9aa1c5c10eb183106136be4f38056108bbfcac98d5b5c3802a068` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr015_s304.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr015_s304.compact.json) | other | 11193 | `40bdef2f85ee73b30059f7936f248734b5bbb0e38aaf6c045fe8725a9c2d3961` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr015_s305.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr015_s305.compact.json) | other | 7782 | `c52ccfdfe5ae249e927d7534bc30bcea0a08436394cacc934caffa7a3e8b043c` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr015_s306.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr015_s306.compact.json) | other | 12487 | `aa8ff1189b5e99393ff8eedcbe9b2f9c375f8f21d36a4d076519edc52be8b2d0` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr015_s307.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr015_s307.compact.json) | other | 10068 | `599876959313a3ce4e59004088946c3b9c7885bdefa117b4b198d22955f1aed6` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr015_s308.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr015_s308.compact.json) | other | 10659 | `30d8027be3731db942a23fbab481fc808c781b633952f25177aff988ff85767f` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr015_s309.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr015_s309.compact.json) | other | 9184 | `c326948fd5c0c889bca0309f5b59ed2b59d27d78acd5732877d352d518e38a79` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr015_s310.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr015_s310.compact.json) | other | 10400 | `a1196d092a15990b336ba4fb8aab89c68702362bf0083604f9aa4aa794614a30` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr025_s301.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr025_s301.compact.json) | other | 66906 | `e88006274584e44379f8133ec1fbd08043b3516bd2a4576ad8bca334fc1875cc` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr025_s302.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr025_s302.compact.json) | other | 50718 | `4977d2eb19235586911852e4a2d48c394dd2d4d1f34e94dad943948677d721f8` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr025_s303.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr025_s303.compact.json) | other | 66169 | `489c5e8f27edf5d30daf0b66843437b8e9bdc78a5ddceb902d04fa51850349df` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr025_s304.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr025_s304.compact.json) | other | 69138 | `3d946bdcaf360b4bb108396fcc2984297fa0ade221364d3e6a90bf314120585a` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr025_s305.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr025_s305.compact.json) | other | 55344 | `d87a45d2fb98a2d81b15803be95f74aafb975a18080ace3fc650af2e2ba8df15` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr025_s306.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr025_s306.compact.json) | other | 66359 | `54413806fab7919f77dc683505256d94fce5d3ac469052bd9c239ccb75d21d5c` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr025_s307.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr025_s307.compact.json) | other | 41377 | `1695828094cf821412350d958f7b9914c4e837e320d9a071062e6e342d951804` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr025_s308.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr025_s308.compact.json) | other | 53211 | `22fc32647d1c4d576818c4d24296241197a3887581ee9e321520dae9c694eb2f` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr025_s309.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr025_s309.compact.json) | other | 60355 | `98993953c3369922041a9285438a0fb55564af9aef9e8cacf347d87253971d95` |
| [`morphogenesis/experiments/L1_field/x112c_f040_thr025_s310.compact.json`](../morphogenesis/experiments/L1_field/x112c_f040_thr025_s310.compact.json) | other | 49922 | `2762a151cadc1ad0fb3f0ac2e7925a2a2cb65e3bc59b2e5727011cce20922bbb` |
| [`morphogenesis/experiments/L1_field/x126_f035_s301.compact.json`](../morphogenesis/experiments/L1_field/x126_f035_s301.compact.json) | other | 327920 | `483321c5b65fccb67760f2ced192ea5e8738745215dd66f1b8e241e2f227249e` |
| [`morphogenesis/experiments/L1_field/x126_f035_s302.compact.json`](../morphogenesis/experiments/L1_field/x126_f035_s302.compact.json) | other | 304424 | `1b194b106f47ac618f6d2c887e88dd624dbc4aee0bd05628df47d53dd84edb68` |
| [`morphogenesis/experiments/L1_field/x126_f035_s303.compact.json`](../morphogenesis/experiments/L1_field/x126_f035_s303.compact.json) | other | 255978 | `7def456fdf72434127e096364d64a426f3790fd390af89d5811152febf66b753` |
| [`morphogenesis/experiments/L1_field/x126_f035_s304.compact.json`](../morphogenesis/experiments/L1_field/x126_f035_s304.compact.json) | other | 342311 | `0c321b209cff6c96cc8f582fa8a2b4a038d956d536ebe9902929e5798652aaf5` |
| [`morphogenesis/experiments/L1_field/x126_f035_s305.compact.json`](../morphogenesis/experiments/L1_field/x126_f035_s305.compact.json) | other | 338537 | `87385efd3768dfb52f9e977346eb09d1ecc3430818849471099344157983831f` |
| [`morphogenesis/experiments/L1_field/x126_f035_s306.compact.json`](../morphogenesis/experiments/L1_field/x126_f035_s306.compact.json) | other | 345330 | `9cf0c05ae2355c8223a354ed5d490bc4a298db9b736cf17ea23d6c8a9f70a40e` |
| [`morphogenesis/experiments/L1_field/x126_f035_s307.compact.json`](../morphogenesis/experiments/L1_field/x126_f035_s307.compact.json) | other | 309990 | `8e066176d48ddcebdd6bbe558ea5461fb2d6e8bf819f70b941901001ec812dbd` |
| [`morphogenesis/experiments/L1_field/x126_f035_s308.compact.json`](../morphogenesis/experiments/L1_field/x126_f035_s308.compact.json) | other | 327422 | `4b4fd024a870c4bca97b543dba14b94be06c16c76ce90433ed2a594c3bd8b3da` |
| [`morphogenesis/experiments/L1_field/x126_f035_s309.compact.json`](../morphogenesis/experiments/L1_field/x126_f035_s309.compact.json) | other | 296787 | `aeb6921abc93feb653672da52de426cc058fac8efbdeffa613c30832b4a6810d` |
| [`morphogenesis/experiments/L1_field/x126_f035_s310.compact.json`](../morphogenesis/experiments/L1_field/x126_f035_s310.compact.json) | other | 275591 | `cdd820a43dfd4d9a997dd88af7c837313fb7a6bbdced33a435002b5422945789` |
| [`morphogenesis/experiments/L1_field/x132_f030_s311.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s311.compact.json) | other | 495080 | `69e813c97bf2e135d67f6d2652142b2409018ffacc8933f28547f724ed255819` |
| [`morphogenesis/experiments/L1_field/x132_f030_s312.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s312.compact.json) | other | 521964 | `9b14480300a85a6e6ee5ba686bf7eb38219d5027e2ef34fee43bdb11015d5533` |
| [`morphogenesis/experiments/L1_field/x132_f030_s313.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s313.compact.json) | other | 538301 | `66f630e53346b0a6e82685d28b063ca327c0853b0537e87a4366aa31a2473ea8` |
| [`morphogenesis/experiments/L1_field/x132_f030_s314.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s314.compact.json) | other | 538865 | `ed82e725255f940fa25f7d210e503039f136e14b25aaf4b9fb4c80d0fa309166` |
| [`morphogenesis/experiments/L1_field/x132_f030_s315.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s315.compact.json) | other | 546985 | `89e49a4de1c67d5694486f10e19a8fb044b9a59f98021ae76362549a71cc0ebf` |
| [`morphogenesis/experiments/L1_field/x132_f030_s316.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s316.compact.json) | other | 557020 | `42936734150f8ec252a393a892bf732422153cf18f30cfd02c514825e93c2623` |
| [`morphogenesis/experiments/L1_field/x132_f030_s317.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s317.compact.json) | other | 537667 | `297c6a371e57341a5eced4964266fc2e1f99d2bb908eb704f439047c3591fb02` |
| [`morphogenesis/experiments/L1_field/x132_f030_s318.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s318.compact.json) | other | 547881 | `0efa7deadc0bbc4878acf30cc53ea9111cf6bae1b2e5691bdfe953519c592e76` |
| [`morphogenesis/experiments/L1_field/x132_f030_s319.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s319.compact.json) | other | 519984 | `00890f68fb63de825274b5340fc6d712cc37222c52ce0fcfe90162ba30d40757` |
| [`morphogenesis/experiments/L1_field/x132_f030_s320.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s320.compact.json) | other | 481521 | `469c53011d8467c16b3299e867f96dbb51b016e1dd23b41b7cdb72369c795cfe` |
| [`morphogenesis/experiments/L1_field/x132_f030_s321.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s321.compact.json) | other | 417411 | `f032384c3d677d273af7c411a64295a80af115f748a5108b3d16e104c9eb0ec7` |
| [`morphogenesis/experiments/L1_field/x132_f030_s322.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s322.compact.json) | other | 511461 | `3fe49a78d693e12100f40a5e34abdf134ab419a8ac72e3625a82e224861ccf52` |
| [`morphogenesis/experiments/L1_field/x132_f030_s323.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s323.compact.json) | other | 497694 | `786e71d9ef1acc2ccec7ec540676e217546446058e19549a6b00a4b8e8ac036c` |
| [`morphogenesis/experiments/L1_field/x132_f030_s324.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s324.compact.json) | other | 531738 | `11cc265fcf8bd444ff628dd0bcb71038bc90186eb9000024aafbc215d8bd5ef4` |
| [`morphogenesis/experiments/L1_field/x132_f030_s325.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s325.compact.json) | other | 540677 | `1352edcaa608f8dff03fddf38c35f786274c32a11e974bfbca1d4765b716dafe` |
| [`morphogenesis/experiments/L1_field/x132_f030_s326.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s326.compact.json) | other | 457673 | `55cb5fdfeda9156cf37be05c1874d4167ea25cc2b4d6916837fddbe0a15c8d59` |
| [`morphogenesis/experiments/L1_field/x132_f030_s327.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s327.compact.json) | other | 536302 | `c810499986eafb2de5c3933d43418c57c86f8e6a51e2d89c4bc53286c9ee0b15` |
| [`morphogenesis/experiments/L1_field/x132_f030_s328.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s328.compact.json) | other | 524148 | `ade7db1e88f8d00bc183a3f7e494b2b5285968e6a3623bf6d2bc181e67c3481e` |
| [`morphogenesis/experiments/L1_field/x132_f030_s329.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s329.compact.json) | other | 471189 | `f4ca78881695956d426b8053710fe47d03b1cd4e7786d2047269ec07ae8533d5` |
| [`morphogenesis/experiments/L1_field/x132_f030_s330.compact.json`](../morphogenesis/experiments/L1_field/x132_f030_s330.compact.json) | other | 521447 | `a87a59a74e1a45622ce11732b4e81c2792d05ddf71c12f1b2c127d51b1a60aa4` |
| [`morphogenesis/experiments/L1_field/x132_f040_s311.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s311.compact.json) | other | 80087 | `bad4993389e5ce427eaf110bdffb37caebb2fcc160b486e267efc7a20d9919fa` |
| [`morphogenesis/experiments/L1_field/x132_f040_s312.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s312.compact.json) | other | 79175 | `abb2ff78554e7ccccc1dac2d416bad4620f644d7f2269660ae7ac97a61739946` |
| [`morphogenesis/experiments/L1_field/x132_f040_s313.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s313.compact.json) | other | 96553 | `84981178be8bbcd129e97d052345bdff92661d41b1848959b0e6c36b3edf69dd` |
| [`morphogenesis/experiments/L1_field/x132_f040_s314.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s314.compact.json) | other | 96781 | `6c31f94b8767268332823935be4aa13862aff7daff09d295a64cf1e92e3924cd` |
| [`morphogenesis/experiments/L1_field/x132_f040_s315.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s315.compact.json) | other | 84153 | `6f320a1dd83a0dfd82dd52cd76a2e064eb4748cda9bb13ff0b3245932baa807b` |
| [`morphogenesis/experiments/L1_field/x132_f040_s316.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s316.compact.json) | other | 98862 | `08f80d1eb86ef83888035773943664d592ba2626be24d82c4f1eb1269c27bf7b` |
| [`morphogenesis/experiments/L1_field/x132_f040_s317.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s317.compact.json) | other | 92433 | `de54bcdfc075ac96e0695e1911f40319115f37d5e04132f4394f46664a7d8c05` |
| [`morphogenesis/experiments/L1_field/x132_f040_s318.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s318.compact.json) | other | 70339 | `f18e3f0972b6b79904410a5be361749933011e5c6c78872eb2dc73a933ac042c` |
| [`morphogenesis/experiments/L1_field/x132_f040_s319.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s319.compact.json) | other | 99395 | `0542872155e7a64f2b48913da988bdc6365e6651227988b17099c2514e4860fd` |
| [`morphogenesis/experiments/L1_field/x132_f040_s320.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s320.compact.json) | other | 97863 | `d9cd0882c4ca5736c046065d20d310ae88c977e55e85cde94f3c1229f5d05a5a` |
| [`morphogenesis/experiments/L1_field/x132_f040_s321.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s321.compact.json) | other | 125222 | `4d89db9c7c15e0d3652991f121d4eff44f303e34b45b739101e2208359f5e5a3` |
| [`morphogenesis/experiments/L1_field/x132_f040_s322.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s322.compact.json) | other | 72655 | `0ec68afedbc5656fad03c0f5a07c58d3a329094e3e36f160ca89f3acdcbfb065` |
| [`morphogenesis/experiments/L1_field/x132_f040_s323.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s323.compact.json) | other | 72465 | `2f7d0661f101eca713abdfb56f12d7831e121aebb6615326d3052d583125c851` |
| [`morphogenesis/experiments/L1_field/x132_f040_s324.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s324.compact.json) | other | 96320 | `f01d083f7ccf070976ea2380fcc0e165e9c2c1e94499c961e3578a777289de13` |
| [`morphogenesis/experiments/L1_field/x132_f040_s325.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s325.compact.json) | other | 96680 | `71f8c6ea7ecbef0554ad54df8b93a3f2be7b5b7a60460d0eb71a5ed87bc7a5d0` |
| [`morphogenesis/experiments/L1_field/x132_f040_s326.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s326.compact.json) | other | 77916 | `45ada5c8a71934499c6aedabfcd8e0622f5ee701906cebb81abdf8da9c6cac59` |
| [`morphogenesis/experiments/L1_field/x132_f040_s327.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s327.compact.json) | other | 75757 | `c53064177265a6f3d17944b2dfb3ed17baf810f51275500d976dbdf2b4aad26e` |
| [`morphogenesis/experiments/L1_field/x132_f040_s328.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s328.compact.json) | other | 73251 | `a0471c8e584382c7368d4944dc5e82490732f495bfc20dea67be339d0e41675b` |
| [`morphogenesis/experiments/L1_field/x132_f040_s329.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s329.compact.json) | other | 103855 | `88f61dda5c471f74817a6c5eff87c38e4b5f6fab1e6a31c66b0bdb83da93993d` |
| [`morphogenesis/experiments/L1_field/x132_f040_s330.compact.json`](../morphogenesis/experiments/L1_field/x132_f040_s330.compact.json) | other | 99437 | `bae5a54934991cd3e99a358cd7b443767ef6d67f6a9bf56e2ce1d8256fadbcab` |
| [`morphogenesis/experiments/L1_field/x134_sep12_s601.compact.json`](../morphogenesis/experiments/L1_field/x134_sep12_s601.compact.json) | other | 561453 | `9d7feb43d35ece89f60799cf17570e5d96167f6efd5d93731fdf24bfe57866dd` |
| [`morphogenesis/experiments/L1_field/x134_sep12_s602.compact.json`](../morphogenesis/experiments/L1_field/x134_sep12_s602.compact.json) | other | 561453 | `6cfa189f8f5fb56d09a3fde1723a8872ce2839612ddbdda83011bc9a8ecea02a` |
| [`morphogenesis/experiments/L1_field/x134_sep12_s603.compact.json`](../morphogenesis/experiments/L1_field/x134_sep12_s603.compact.json) | other | 561453 | `4bf3360f3f5782c29cb3477615b2e3cae215717b0d7ad66ed427eb7c33e385f7` |
| [`morphogenesis/experiments/L1_field/x134_sep12_s604.compact.json`](../morphogenesis/experiments/L1_field/x134_sep12_s604.compact.json) | other | 561453 | `00573224b6d9e219fa09ba16f7fcbec62ea65f09b05e565e814e8d9a513b137f` |
| [`morphogenesis/experiments/L1_field/x134_sep12_s605.compact.json`](../morphogenesis/experiments/L1_field/x134_sep12_s605.compact.json) | other | 561453 | `df731d3ae91e0c3be5acb15fc886626d2b37ed1f07c113458c685de483715ac1` |
| [`morphogenesis/experiments/L1_field/x134_sep18_s601.compact.json`](../morphogenesis/experiments/L1_field/x134_sep18_s601.compact.json) | other | 518837 | `3e875317693b2a9e65b7411069ae520aa2269d9654b419eefbfe973980afdd17` |
| [`morphogenesis/experiments/L1_field/x134_sep18_s602.compact.json`](../morphogenesis/experiments/L1_field/x134_sep18_s602.compact.json) | other | 518837 | `c52e31eb57cc39a8cc2f5f1ebff17ac7e2d92bb2a8094f93c2b3d212a69ee72c` |
| [`morphogenesis/experiments/L1_field/x134_sep18_s603.compact.json`](../morphogenesis/experiments/L1_field/x134_sep18_s603.compact.json) | other | 518837 | `cc9369e47ca0669ca7cd18baef7f1238d118e3e2123c4faaf7cfdbe0d3d6edc0` |
| [`morphogenesis/experiments/L1_field/x134_sep18_s604.compact.json`](../morphogenesis/experiments/L1_field/x134_sep18_s604.compact.json) | other | 518837 | `b2c4717a80ce4502ff79e2ef109101a817d9a12cc947d7acc43d0594c8b2cace` |
| [`morphogenesis/experiments/L1_field/x134_sep18_s605.compact.json`](../morphogenesis/experiments/L1_field/x134_sep18_s605.compact.json) | other | 518837 | `6ef9954b1c446ef38426db4e9551add63a43fa142c42fc655b3414defed132ca` |
| [`morphogenesis/experiments/L1_field/x134_sep24_s601.compact.json`](../morphogenesis/experiments/L1_field/x134_sep24_s601.compact.json) | other | 585634 | `6d6183d3f8578a5eddea49150e96e375ec63b73a9bf139a18a6a19779aa87e26` |
| [`morphogenesis/experiments/L1_field/x134_sep24_s602.compact.json`](../morphogenesis/experiments/L1_field/x134_sep24_s602.compact.json) | other | 585634 | `d7156e874bd43ffb3682a580ead0cce8cfdf122aed56c173fa5704eda152c86d` |
| [`morphogenesis/experiments/L1_field/x134_sep24_s603.compact.json`](../morphogenesis/experiments/L1_field/x134_sep24_s603.compact.json) | other | 585634 | `ded3199a745010ffce7f775095ef0417ccffe70e67957394fa2574a40781fb4c` |
| [`morphogenesis/experiments/L1_field/x134_sep24_s604.compact.json`](../morphogenesis/experiments/L1_field/x134_sep24_s604.compact.json) | other | 585634 | `3420fea35d78168d3719d74194f778e3b3a6772c3a5092bc8f8dcc87def75967` |
| [`morphogenesis/experiments/L1_field/x134_sep24_s605.compact.json`](../morphogenesis/experiments/L1_field/x134_sep24_s605.compact.json) | other | 585634 | `d670228628c233a2ceaa1cd7a2a85f6a54ae5b8f7fa88949dc5cfd7e96e47026` |
| [`morphogenesis/experiments/L1_field/x134_sep30_s601.compact.json`](../morphogenesis/experiments/L1_field/x134_sep30_s601.compact.json) | other | 537485 | `fbec33a4de8b3a71b943774ab0aa9359f7ad68b43e3c1e75bb38ff58f003c42c` |
| [`morphogenesis/experiments/L1_field/x134_sep30_s602.compact.json`](../morphogenesis/experiments/L1_field/x134_sep30_s602.compact.json) | other | 537485 | `8da9221d480519c3718dbb9c5fd7702adc21f99559bdc9668e8201a16706b8b2` |
| [`morphogenesis/experiments/L1_field/x134_sep30_s603.compact.json`](../morphogenesis/experiments/L1_field/x134_sep30_s603.compact.json) | other | 537485 | `71373f6868d4a65ae2d89e8f17dee715ace4191382e2dbe5c17bb701010154be` |
| [`morphogenesis/experiments/L1_field/x134_sep30_s604.compact.json`](../morphogenesis/experiments/L1_field/x134_sep30_s604.compact.json) | other | 537485 | `193ab90a0a5a728db37e54e0368b133ef5b6015def2634232f7b722b1148005e` |
| [`morphogenesis/experiments/L1_field/x134_sep30_s605.compact.json`](../morphogenesis/experiments/L1_field/x134_sep30_s605.compact.json) | other | 537485 | `e7c91c0853d89062b1191f80032d7b19993dcb0b69cd840e75b992f207dfee40` |
| [`morphogenesis/experiments/L1_field/x134_sep36_s601.compact.json`](../morphogenesis/experiments/L1_field/x134_sep36_s601.compact.json) | other | 509365 | `ebc940306c30c4766d515e3995cff129d7884be1f63f042fc885084b683cc5a3` |
| [`morphogenesis/experiments/L1_field/x134_sep36_s602.compact.json`](../morphogenesis/experiments/L1_field/x134_sep36_s602.compact.json) | other | 509365 | `b030ce9d2c7afa08d4d8e576137e376a0eb194ff041ed7f0a58b434a11c9462e` |
| [`morphogenesis/experiments/L1_field/x134_sep36_s603.compact.json`](../morphogenesis/experiments/L1_field/x134_sep36_s603.compact.json) | other | 509365 | `85c4149e62bf892fa394fa6666937dd1e12433be077514052fb09a80a2e22b84` |
| [`morphogenesis/experiments/L1_field/x134_sep36_s604.compact.json`](../morphogenesis/experiments/L1_field/x134_sep36_s604.compact.json) | other | 509365 | `e6c76fb5d39e3445539f9199bfad52bdd73d2bc9dd87d31abe62a2eff70eda15` |
| [`morphogenesis/experiments/L1_field/x134_sep36_s605.compact.json`](../morphogenesis/experiments/L1_field/x134_sep36_s605.compact.json) | other | 509365 | `b725db51812f4f4f2d66bf7f40a6698c43cf4dd83763ad1468e68c5d2476c356` |
| [`morphogenesis/experiments/L1_field/x134_sep6_s601.compact.json`](../morphogenesis/experiments/L1_field/x134_sep6_s601.compact.json) | other | 549521 | `f35c5a8409f9e2a60eb8d321497528e2082a504befaa220850b6059f5e5abb98` |
| [`morphogenesis/experiments/L1_field/x134_sep6_s602.compact.json`](../morphogenesis/experiments/L1_field/x134_sep6_s602.compact.json) | other | 549521 | `6e42cae0bfd64410f2893b15569e73daa871646111a22dfb905d3b58f91e95d2` |
| [`morphogenesis/experiments/L1_field/x134_sep6_s603.compact.json`](../morphogenesis/experiments/L1_field/x134_sep6_s603.compact.json) | other | 549521 | `b1d92d39281cf537c1a7f218ed6e6cb45df835a0049de17063465c661f7814dc` |
| [`morphogenesis/experiments/L1_field/x134_sep6_s604.compact.json`](../morphogenesis/experiments/L1_field/x134_sep6_s604.compact.json) | other | 549521 | `9b2f132d723667c172f38907b4efdeaf174164ed524fb31a35112f67438c8ef3` |
| [`morphogenesis/experiments/L1_field/x134_sep6_s605.compact.json`](../morphogenesis/experiments/L1_field/x134_sep6_s605.compact.json) | other | 549521 | `b04841da1c7be5477506954878dfc5aa765eaaf45b949ddae925a351b73569cb` |
| [`morphogenesis/experiments/L1_field/x134_sep8_s601.compact.json`](../morphogenesis/experiments/L1_field/x134_sep8_s601.compact.json) | other | 573213 | `ad024b1589c638e9f477cf4ed0e7f6968cc385ff02744a76066c88d1af0e8728` |
| [`morphogenesis/experiments/L1_field/x134_sep8_s602.compact.json`](../morphogenesis/experiments/L1_field/x134_sep8_s602.compact.json) | other | 573213 | `abb2890efbd91f9a0865a4d7a164f3aa0ee99c84a0b88ef024456649d6cbe9d2` |
| [`morphogenesis/experiments/L1_field/x134_sep8_s603.compact.json`](../morphogenesis/experiments/L1_field/x134_sep8_s603.compact.json) | other | 573213 | `fc5399f0cc0a579fe009dcf83339dfd5faba245c26f52e303737a790d5c87abe` |
| [`morphogenesis/experiments/L1_field/x134_sep8_s604.compact.json`](../morphogenesis/experiments/L1_field/x134_sep8_s604.compact.json) | other | 573213 | `a1708acedf5eae9d89d8c2d6b14da65eaadfa576ec2035860436fe7cca918c4c` |
| [`morphogenesis/experiments/L1_field/x134_sep8_s605.compact.json`](../morphogenesis/experiments/L1_field/x134_sep8_s605.compact.json) | other | 573213 | `0a65966c538707d20b2b3270d1c221c54daa32b81ada1ecf93f6d0830124897a` |
| [`morphogenesis/experiments/L1_field/x134b_sep12_s601.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep12_s601.compact.json) | other | 529614 | `8f692a34b171f1d85620f3310135baadc9226d15677f95982e140da9bc154c98` |
| [`morphogenesis/experiments/L1_field/x134b_sep12_s602.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep12_s602.compact.json) | other | 529157 | `c32685d824e2fbd4cb68d5037affd41c484bfd972622913e626232e020e144d0` |
| [`morphogenesis/experiments/L1_field/x134b_sep12_s603.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep12_s603.compact.json) | other | 562186 | `df7e070c3e5a7aba9332dffb77933ee81867c98b1e82e83e2b0a33029436d460` |
| [`morphogenesis/experiments/L1_field/x134b_sep12_s604.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep12_s604.compact.json) | other | 512190 | `bbe76956f572751d456862d3b243ed093cc2d1b356f6cc6c86830b43209fa37c` |
| [`morphogenesis/experiments/L1_field/x134b_sep12_s605.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep12_s605.compact.json) | other | 512374 | `2692acce2927acb741caa5364f13c3f9d43414f53776a9bf25c0beade37ba525` |
| [`morphogenesis/experiments/L1_field/x134b_sep15_s601.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep15_s601.compact.json) | other | 565706 | `5cd35225e2315296411e8e7fe6202bf3363643e89a7e4b18eaf18083b962579b` |
| [`morphogenesis/experiments/L1_field/x134b_sep15_s602.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep15_s602.compact.json) | other | 496636 | `765b5639bcd22553ecda755bfc66e922f9046f590ab8e6f21acfe40d80dca12c` |
| [`morphogenesis/experiments/L1_field/x134b_sep15_s603.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep15_s603.compact.json) | other | 581693 | `1cebff09e4b904b4ead883e82e037b93ada1a6e5a1010dda6e9e7b60e34f2f0a` |
| [`morphogenesis/experiments/L1_field/x134b_sep15_s604.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep15_s604.compact.json) | other | 603019 | `ccc27cde1c9b26d476d8c29854b1d497e60467f215f0d804291c04c09c3bf676` |
| [`morphogenesis/experiments/L1_field/x134b_sep15_s605.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep15_s605.compact.json) | other | 604500 | `e558d42c34d12280500318ccb098f2787c44335547cd63484b960a3703b92290` |
| [`morphogenesis/experiments/L1_field/x134b_sep18_s601.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep18_s601.compact.json) | other | 606358 | `36628432fee3df6c6713ca24f327719b3ff7062932e45c343d3d7ca576da4753` |
| [`morphogenesis/experiments/L1_field/x134b_sep18_s602.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep18_s602.compact.json) | other | 576841 | `d182954fdba6adb78744ecf57bcf70334c107c7fbe9277e6da0ea89155b41700` |
| [`morphogenesis/experiments/L1_field/x134b_sep18_s603.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep18_s603.compact.json) | other | 519388 | `bf8db8398acabee651dfd498a2350e5ff0973424ccc7d4802ec35a8641cb8731` |
| [`morphogenesis/experiments/L1_field/x134b_sep18_s604.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep18_s604.compact.json) | other | 549797 | `8bd1f722617492006e0cfa44de4e3a5bfdc451d506460f279b4919b5ed17f50a` |
| [`morphogenesis/experiments/L1_field/x134b_sep18_s605.compact.json`](../morphogenesis/experiments/L1_field/x134b_sep18_s605.compact.json) | other | 551249 | `7251c6a837fc13a5532455ca5ba48f4c6f244447086bcd213027845ded4e9ad8` |
| [`morphogenesis/experiments/L1_field/x135_sep0_s601.compact.json`](../morphogenesis/experiments/L1_field/x135_sep0_s601.compact.json) | other | 108423 | `f2d356b072bad2c665444404dbee50a77a75e010a527a6d70294505e9f1bce8b` |
| [`morphogenesis/experiments/L1_field/x135_sep0_s602.compact.json`](../morphogenesis/experiments/L1_field/x135_sep0_s602.compact.json) | other | 108423 | `097f55048a4df559d2272a55140bac4652a020d6a9b34d779d5a70c74953ef0d` |
| [`morphogenesis/experiments/L1_field/x135_sep0_s603.compact.json`](../morphogenesis/experiments/L1_field/x135_sep0_s603.compact.json) | other | 108423 | `f90198d467c2a06a8f9c6e3ef644e18fdc5d46642401b60c03005f8f572f715e` |
| [`morphogenesis/experiments/L1_field/x135_sep0_s604.compact.json`](../morphogenesis/experiments/L1_field/x135_sep0_s604.compact.json) | other | 108423 | `7cb785e310bd736a8a3f2a1996bf264fbd1c91a621e971bb6880c07ed86d0cad` |
| [`morphogenesis/experiments/L1_field/x135_sep0_s605.compact.json`](../morphogenesis/experiments/L1_field/x135_sep0_s605.compact.json) | other | 108423 | `046f58244fc9fec67f3c6ff5bbd182abb6df021a9544d319cd6ba100d286a3c9` |
| [`morphogenesis/experiments/L1_field/x135_sep12_s601.compact.json`](../morphogenesis/experiments/L1_field/x135_sep12_s601.compact.json) | other | 82708 | `4457ebbcfcf24e950f36cccab4ea241c6d5bebd5388dfbdff6ee1e3dbe75d117` |
| [`morphogenesis/experiments/L1_field/x135_sep8_s601.compact.json`](../morphogenesis/experiments/L1_field/x135_sep8_s601.compact.json) | other | 95945 | `00c3ec27058b1df25850aa559abc09da7cb3461c63734e05292f82f2dbeace62` |
| [`morphogenesis/experiments/L1_field/x135_sep8_s602.compact.json`](../morphogenesis/experiments/L1_field/x135_sep8_s602.compact.json) | other | 95945 | `e5c153e29780948ecb550efcce2151272ba572e920ee7c3b35609ecef0681bb2` |
| [`morphogenesis/experiments/L1_field/x135_sep8_s603.compact.json`](../morphogenesis/experiments/L1_field/x135_sep8_s603.compact.json) | other | 95945 | `c29525f91f5a6f87388a106dd83118e77cc3c93d49df5be1184698ef2e71af23` |
| [`morphogenesis/experiments/L1_field/x135_sep8_s604.compact.json`](../morphogenesis/experiments/L1_field/x135_sep8_s604.compact.json) | other | 95945 | `8cc7ee46962523f0d146daf627c883790417fdea7fa77ae2be8655ef7b1e7f71` |
| [`morphogenesis/experiments/L1_field/x135_sep8_s605.compact.json`](../morphogenesis/experiments/L1_field/x135_sep8_s605.compact.json) | other | 95945 | `0a272d066bea20896c5f749381778ec07a860cbce4b5acf9513f5afcd8ad2da5` |
| [`morphogenesis/experiments/L1_field/x136_sep14_s601.compact.json`](../morphogenesis/experiments/L1_field/x136_sep14_s601.compact.json) | other | 597779 | `9aeb2a4b87fabff8470cba1aff93c3218ecdc467c468bfb534f06024fa55f34b` |
| [`morphogenesis/experiments/L1_field/x136_sep14_s602.compact.json`](../morphogenesis/experiments/L1_field/x136_sep14_s602.compact.json) | other | 564965 | `13f63dece00124ccbf6dabc23996e1ae3b05deb4e42311d608ede91ba5c33600` |
| [`morphogenesis/experiments/L1_field/x136_sep14_s603.compact.json`](../morphogenesis/experiments/L1_field/x136_sep14_s603.compact.json) | other | 574908 | `40e215c8dbed5fbe2f85b8c08d1a4db5bdf91876e750fdffea731cff435478ba` |
| [`morphogenesis/experiments/L1_field/x136_sep14_s604.compact.json`](../morphogenesis/experiments/L1_field/x136_sep14_s604.compact.json) | other | 534057 | `6bb11c9b2e3c468c47a151b6ec1d660b68985bacf9aedc29e9c04b9e0331dd2f` |
| [`morphogenesis/experiments/L1_field/x136_sep14_s605.compact.json`](../morphogenesis/experiments/L1_field/x136_sep14_s605.compact.json) | other | 533154 | `af0513347628962c12981f7ce0962f979f150430d8e143f3eb6785e148880579` |
| [`morphogenesis/experiments/L1_field/x136_sep16_s601.compact.json`](../morphogenesis/experiments/L1_field/x136_sep16_s601.compact.json) | other | 511020 | `e042301880eb3c2f8f70d75b96d534d82ec5de200ec1bc357c348d7233eaace4` |
| [`morphogenesis/experiments/L1_field/x136_sep16_s602.compact.json`](../morphogenesis/experiments/L1_field/x136_sep16_s602.compact.json) | other | 529887 | `1845b01264aee63e3b2ebcb2cd4c38e8b8a6aab475df92770b69788ab3a320bc` |
| [`morphogenesis/experiments/L1_field/x136_sep16_s603.compact.json`](../morphogenesis/experiments/L1_field/x136_sep16_s603.compact.json) | other | 534033 | `2a7f62807401fde96a55064bdd89239df3fc8ef6cd790a3ed1ec479100dee530` |
| [`morphogenesis/experiments/L1_field/x136_sep16_s604.compact.json`](../morphogenesis/experiments/L1_field/x136_sep16_s604.compact.json) | other | 578111 | `7c2db13a4dfed4e9290462e0ff4f5b2e4b547a531bc2b7386059b1e3d89938f2` |
| [`morphogenesis/experiments/L1_field/x136_sep16_s605.compact.json`](../morphogenesis/experiments/L1_field/x136_sep16_s605.compact.json) | other | 578356 | `04b88aeeda086533a077b90b3c097c04d64d3b285e31320f135c65882bbce11a` |
| [`morphogenesis/experiments/L1_field/x136_sep17_s601.compact.json`](../morphogenesis/experiments/L1_field/x136_sep17_s601.compact.json) | other | 584277 | `7f088ca965331f2e3b3da2e55454093d5e6df146e6d4a319ba485a17a0e85657` |
| [`morphogenesis/experiments/L1_field/x136_sep17_s602.compact.json`](../morphogenesis/experiments/L1_field/x136_sep17_s602.compact.json) | other | 586978 | `5c6b6605df5d819b0e0fdd7199bcad63aa754d328a15cf613a1fef3b43f6203b` |
| [`morphogenesis/experiments/L1_field/x136_sep17_s603.compact.json`](../morphogenesis/experiments/L1_field/x136_sep17_s603.compact.json) | other | 595594 | `8d2645804e7961c427a460bd70d48b53a2af5de11b63397cced9bb22eeb3946f` |
| [`morphogenesis/experiments/L1_field/x136_sep17_s604.compact.json`](../morphogenesis/experiments/L1_field/x136_sep17_s604.compact.json) | other | 583293 | `2b729d04268141df6e649bece1845b7a12164b266e8be176759fc76590c58b13` |
| [`morphogenesis/experiments/L1_field/x136_sep17_s605.compact.json`](../morphogenesis/experiments/L1_field/x136_sep17_s605.compact.json) | other | 583490 | `19887b6830a7e3391275e94fdbc2210868ba5a9079ff40ba8494311138aa7e3e` |
| [`morphogenesis/experiments/L1_field/x138_sep0_s601.compact.json`](../morphogenesis/experiments/L1_field/x138_sep0_s601.compact.json) | other | 490654 | `a9d28960e0336ef24797bc89571281415009bfc1142e4ce24dfde656fad8ce80` |
| [`morphogenesis/experiments/L1_field/x138_sep0_s602.compact.json`](../morphogenesis/experiments/L1_field/x138_sep0_s602.compact.json) | other | 394484 | `b4faf4acb67a0f70d3285aa2c28b40de1a205594761ce0bd31bf40d1392dc840` |
| [`morphogenesis/experiments/L1_field/x138_sep0_s603.compact.json`](../morphogenesis/experiments/L1_field/x138_sep0_s603.compact.json) | other | 579886 | `7d54c6504c03c65ebeb408e0e8bade4bd1e80b49bf3a416dc07f9a5047ba1194` |
| [`morphogenesis/experiments/L1_field/x138_sep0_s604.compact.json`](../morphogenesis/experiments/L1_field/x138_sep0_s604.compact.json) | other | 449970 | `541a41eb681976644ac7b93c080420f2ce9ddd8daac055b1a07e09e6cde45b59` |
| [`morphogenesis/experiments/L1_field/x138_sep0_s605.compact.json`](../morphogenesis/experiments/L1_field/x138_sep0_s605.compact.json) | other | 450214 | `100f0e895387c2408beb054f8e6f2649a16ce97797ed9a37bc24b297b321230d` |
| [`morphogenesis/experiments/L1_field/x138_sep16_s601.compact.json`](../morphogenesis/experiments/L1_field/x138_sep16_s601.compact.json) | other | 599216 | `88d020c2d83d0f0ef5b2e22bbe30bfdd9bf02f4170af11667cd5f8bc0f157129` |
| [`morphogenesis/experiments/L1_field/x138_sep16_s602.compact.json`](../morphogenesis/experiments/L1_field/x138_sep16_s602.compact.json) | other | 588773 | `5f15c2d0bc68af5ce5d4f411733796132ade7904ea73125cb2d3e0ff348bc1d9` |
| [`morphogenesis/experiments/L1_field/x138_sep16_s603.compact.json`](../morphogenesis/experiments/L1_field/x138_sep16_s603.compact.json) | other | 574654 | `a4cded89fab6a8397e8b337a4f2d2e9442c3852c81a476b069d8cb0b8ca2c10b` |
| [`morphogenesis/experiments/L1_field/x138_sep16_s604.compact.json`](../morphogenesis/experiments/L1_field/x138_sep16_s604.compact.json) | other | 538865 | `e9089b355b4987ac6e3df6bb1e1a14caae390dad2f812b1c1838993fbfc2e127` |
| [`morphogenesis/experiments/L1_field/x138_sep16_s605.compact.json`](../morphogenesis/experiments/L1_field/x138_sep16_s605.compact.json) | other | 538895 | `f0f95df5028b036a4bd754176eaf88af6d6b4a5f97a7784fadfde055e3844168` |
| [`morphogenesis/experiments/L1_field/x138_sep18_s601.compact.json`](../morphogenesis/experiments/L1_field/x138_sep18_s601.compact.json) | other | 518898 | `002f0398505e32b8580e2440f00d7db71dbdf398be3fdbe0b7203b716e3f1cc7` |
| [`morphogenesis/experiments/L1_field/x138_sep18_s602.compact.json`](../morphogenesis/experiments/L1_field/x138_sep18_s602.compact.json) | other | 598756 | `04b46d65ea7d50ab785a7d10d62e053e4e82dec9c0a2df651ca00fb8f37ce0df` |
| [`morphogenesis/experiments/L1_field/x138_sep18_s603.compact.json`](../morphogenesis/experiments/L1_field/x138_sep18_s603.compact.json) | other | 556530 | `52cf2f660d0adf6b2b91bd9136f891b9c49c13d70c8c890d2b4e3db053a6847b` |
| [`morphogenesis/experiments/L1_field/x138_sep18_s604.compact.json`](../morphogenesis/experiments/L1_field/x138_sep18_s604.compact.json) | other | 536929 | `3c08e104b3287ef61fd8cb9c17789e513666ddad2659a27732cebf89b760b42b` |
| [`morphogenesis/experiments/L1_field/x138_sep18_s605.compact.json`](../morphogenesis/experiments/L1_field/x138_sep18_s605.compact.json) | other | 537440 | `097b9aad0d0f499ee2a8e775959acc36632022488625268716f03e8eb8ef8bb7` |
| [`morphogenesis/experiments/L1_field/x138_sep20_s601.compact.json`](../morphogenesis/experiments/L1_field/x138_sep20_s601.compact.json) | other | 607346 | `d960694074a923e7767009b9f519acff8833757dfcaf86ec2f64bc40811bf3d1` |
| [`morphogenesis/experiments/L1_field/x138_sep20_s602.compact.json`](../morphogenesis/experiments/L1_field/x138_sep20_s602.compact.json) | other | 608965 | `dee1d1993122a34a5fc9bb16184a7378e9159a35640243f1cadc3324ca226b5c` |
| [`morphogenesis/experiments/L1_field/x138_sep20_s603.compact.json`](../morphogenesis/experiments/L1_field/x138_sep20_s603.compact.json) | other | 614115 | `0012a33ad7859606559de62d624e068f3f5d2215a29a2af6edc0e4ed2b9e5888` |
| [`morphogenesis/experiments/L1_field/x138_sep20_s604.compact.json`](../morphogenesis/experiments/L1_field/x138_sep20_s604.compact.json) | other | 573143 | `d35b3ece9db00d7a7a72c660efc03ec6e8ffad8a53a4f02cbef56882be8c8225` |
| [`morphogenesis/experiments/L1_field/x138_sep20_s605.compact.json`](../morphogenesis/experiments/L1_field/x138_sep20_s605.compact.json) | other | 573191 | `b5b3d44ab8ad74e48826a6c88f7a1518989e9ca5ab2fc3d2cf58daf710c48baa` |
| [`morphogenesis/experiments/L1_field/x138_sep24_s601.compact.json`](../morphogenesis/experiments/L1_field/x138_sep24_s601.compact.json) | other | 564482 | `3cea894809316ef2c9d409ce2acdd73d7a383100fed084602a05d1cff42baab2` |
| [`morphogenesis/experiments/L1_field/x138_sep24_s602.compact.json`](../morphogenesis/experiments/L1_field/x138_sep24_s602.compact.json) | other | 545870 | `5c57e3e9326853dc47cbe689d3d5cd417e4e207f634131fa1089f3ab18cb905a` |
| [`morphogenesis/experiments/L1_field/x138_sep24_s603.compact.json`](../morphogenesis/experiments/L1_field/x138_sep24_s603.compact.json) | other | 578500 | `b58ecb201a0ea92a996132832314eb3b95bb7ebd4ba7a04e5e4a0b04039ffcb8` |
| [`morphogenesis/experiments/L1_field/x138_sep24_s604.compact.json`](../morphogenesis/experiments/L1_field/x138_sep24_s604.compact.json) | other | 535120 | `10d2bd8a4857518206a2b50cb4cb5a453a26493cfd1e4005a0b2e64284d172c4` |
| [`morphogenesis/experiments/L1_field/x138_sep24_s605.compact.json`](../morphogenesis/experiments/L1_field/x138_sep24_s605.compact.json) | other | 535811 | `abc9333375359fe2b472422c4ac61c979dba8206ea4a49a7756df584bb47e62f` |
| [`morphogenesis/experiments/L1_field/x138_sep32_s601.compact.json`](../morphogenesis/experiments/L1_field/x138_sep32_s601.compact.json) | other | 605531 | `36e9bd61876ff15f6c4d1d216e134f2ff24f6efadc04bae6e6b494fb2f9cb859` |
| [`morphogenesis/experiments/L1_field/x138_sep32_s602.compact.json`](../morphogenesis/experiments/L1_field/x138_sep32_s602.compact.json) | other | 626643 | `4306e3ed73e4ee50dd1b3ae77587ad307837655e41c6473707105b258505dbcd` |
| [`morphogenesis/experiments/L1_field/x138_sep32_s603.compact.json`](../morphogenesis/experiments/L1_field/x138_sep32_s603.compact.json) | other | 549227 | `b7d9afeb45b1c0aea0b6bda1873dde988f658f1c9251919a586b000c133e2ace` |
| [`morphogenesis/experiments/L1_field/x138_sep32_s604.compact.json`](../morphogenesis/experiments/L1_field/x138_sep32_s604.compact.json) | other | 565718 | `8f19c6f64cbded29c9bab839426a626bfd92f828f691d7aed798b34498026381` |
| [`morphogenesis/experiments/L1_field/x138_sep32_s605.compact.json`](../morphogenesis/experiments/L1_field/x138_sep32_s605.compact.json) | other | 563720 | `89b0f1aaac60bbbca79b757b39c9fda56b0bc8c8afe291819fac5b1d364fa2fe` |
| [`morphogenesis/experiments/L1_field/x138_sep40_s601.compact.json`](../morphogenesis/experiments/L1_field/x138_sep40_s601.compact.json) | other | 609767 | `a175a23135f880be9ad46c5e700baf0bcb4a39aed26da28e2e8f63ec92731393` |
| [`morphogenesis/experiments/L1_field/x138_sep40_s602.compact.json`](../morphogenesis/experiments/L1_field/x138_sep40_s602.compact.json) | other | 624630 | `8dc5d9f4f2e9086fbbeccb5150da181b68819a6107f91a80d54187fbb04f8ea0` |
| [`morphogenesis/experiments/L1_field/x138_sep40_s603.compact.json`](../morphogenesis/experiments/L1_field/x138_sep40_s603.compact.json) | other | 583195 | `08d004ec982509bc5935d5062cef9d4fc8aa80864d8572a547fa8e50b41705c1` |
| [`morphogenesis/experiments/L1_field/x138_sep40_s604.compact.json`](../morphogenesis/experiments/L1_field/x138_sep40_s604.compact.json) | other | 584728 | `5f4572fcb6e6b127b4148b840762a1417c190a1b782f497ea474401ebf861485` |
| [`morphogenesis/experiments/L1_field/x138_sep40_s605.compact.json`](../morphogenesis/experiments/L1_field/x138_sep40_s605.compact.json) | other | 583522 | `86520ab797e5437e9aa18d27b120adf250325d9df79ddb778a7ac301053ed6be` |
| [`morphogenesis/experiments/L1_field/x139_sep10_s601.compact.json`](../morphogenesis/experiments/L1_field/x139_sep10_s601.compact.json) | other | 529172 | `d8707ebf0a2c07a7c8646ed6033217af9b124ccc5f642c59080908efc424c3a9` |
| [`morphogenesis/experiments/L1_field/x139_sep10_s602.compact.json`](../morphogenesis/experiments/L1_field/x139_sep10_s602.compact.json) | other | 538520 | `caa3d27a3c0628e7f3c3d1718ef6c5d4b7e43b29888a6b0bcc93902bdde173fe` |
| [`morphogenesis/experiments/L1_field/x139_sep10_s603.compact.json`](../morphogenesis/experiments/L1_field/x139_sep10_s603.compact.json) | other | 541648 | `1b8bb77f7cfd39d396d9bbda91fd007990c80a3b169ee0ba9f55cba90f9a8ddb` |
| [`morphogenesis/experiments/L1_field/x139_sep10_s604.compact.json`](../morphogenesis/experiments/L1_field/x139_sep10_s604.compact.json) | other | 580706 | `b2bc039a12d3ae69fa19550689d4a9f8540f6dc77b0838c154ca9bfb2f95aa1c` |
| [`morphogenesis/experiments/L1_field/x139_sep10_s605.compact.json`](../morphogenesis/experiments/L1_field/x139_sep10_s605.compact.json) | other | 579546 | `487fc49e2cda613163cf6a0b3e2fb71fec32baf46a677261583c073e822aa5ce` |
| [`morphogenesis/experiments/L1_field/x139_sep11_s601.compact.json`](../morphogenesis/experiments/L1_field/x139_sep11_s601.compact.json) | other | 570149 | `09d00165548cc35c30523d2242c13955128f37a375f0d6bd02bed63716901b96` |
| [`morphogenesis/experiments/L1_field/x139_sep11_s602.compact.json`](../morphogenesis/experiments/L1_field/x139_sep11_s602.compact.json) | other | 577900 | `bf7a82e3adbddeb820659ce578f415630a40f6e0d70a16b8fc3c652ca3fe96b4` |
| [`morphogenesis/experiments/L1_field/x139_sep11_s603.compact.json`](../morphogenesis/experiments/L1_field/x139_sep11_s603.compact.json) | other | 545011 | `e413e4492a4ddf0f114aad5eac18930ed2112522a07d49c92f077ed15f4955a5` |
| [`morphogenesis/experiments/L1_field/x139_sep11_s604.compact.json`](../morphogenesis/experiments/L1_field/x139_sep11_s604.compact.json) | other | 575054 | `b6aeb32113daefb591aa22e16427b4420cb46e6399a9a4b6246585f3230729fe` |
| [`morphogenesis/experiments/L1_field/x139_sep11_s605.compact.json`](../morphogenesis/experiments/L1_field/x139_sep11_s605.compact.json) | other | 574824 | `4961d6905e54d05a7128cfb72de9ae435f446e3daabc6c32585c83b5c1d43ed7` |
| [`morphogenesis/experiments/L1_field/x139_sep7_s601.compact.json`](../morphogenesis/experiments/L1_field/x139_sep7_s601.compact.json) | other | 534826 | `b7604d76c95c7e63c7786788e0269c64c83f7e5845bac7770a84db1df1e628bf` |
| [`morphogenesis/experiments/L1_field/x139_sep7_s602.compact.json`](../morphogenesis/experiments/L1_field/x139_sep7_s602.compact.json) | other | 534698 | `61139504f79288bf26e499deeacc2a91f35bfa18769cf833f4f4917db8c4ad29` |
| [`morphogenesis/experiments/L1_field/x139_sep7_s603.compact.json`](../morphogenesis/experiments/L1_field/x139_sep7_s603.compact.json) | other | 579997 | `8d998185db2fd3262ef7b8ed44942e699f0eba6a3916242ee769fe4295ba2c93` |
| [`morphogenesis/experiments/L1_field/x139_sep7_s604.compact.json`](../morphogenesis/experiments/L1_field/x139_sep7_s604.compact.json) | other | 559836 | `ab045a0c17b8020d929b20c7b29da0df6dbb15aaa0df7cd98797da286de31cdd` |
| [`morphogenesis/experiments/L1_field/x139_sep7_s605.compact.json`](../morphogenesis/experiments/L1_field/x139_sep7_s605.compact.json) | other | 560609 | `08037040bce185251e58b6136972f6f07cdb57a209a4fa4b0aade2482553cf00` |
| [`morphogenesis/experiments/L1_field/x139_sep8_s601.compact.json`](../morphogenesis/experiments/L1_field/x139_sep8_s601.compact.json) | other | 568457 | `e876de57cf03d8d5b001f6dc14826ec2702388588789dacc12723134df908888` |
| [`morphogenesis/experiments/L1_field/x139_sep8_s602.compact.json`](../morphogenesis/experiments/L1_field/x139_sep8_s602.compact.json) | other | 555659 | `25649edfea69cd5fb2962663f005e070f32d5df41aa6c58b6a4ebe55048d3715` |
| [`morphogenesis/experiments/L1_field/x139_sep8_s603.compact.json`](../morphogenesis/experiments/L1_field/x139_sep8_s603.compact.json) | other | 573447 | `b6df8929abcfd0a7ffb4d8f49ee26b42986018fce351ac8c8dc677c2d773d9e8` |
| [`morphogenesis/experiments/L1_field/x139_sep8_s604.compact.json`](../morphogenesis/experiments/L1_field/x139_sep8_s604.compact.json) | other | 587329 | `f8d8bd5d73450d785b13050923b68bcf4e1a74cd4be7deba4d03fe9d166159b5` |
| [`morphogenesis/experiments/L1_field/x139_sep8_s605.compact.json`](../morphogenesis/experiments/L1_field/x139_sep8_s605.compact.json) | other | 588237 | `a9760612c612244a5b7ce992d33bf6aa019eb917a195f1e59527795b0ee303e2` |
| [`morphogenesis/experiments/L1_field/x140_sep0_s601.compact.json`](../morphogenesis/experiments/L1_field/x140_sep0_s601.compact.json) | other | 545414 | `e6b4c36dcc5fc2d754f30e76e106926b2817b7a8a0b654dc8cf34cc5eae3d68b` |
| [`morphogenesis/experiments/L1_field/x140_sep0_s602.compact.json`](../morphogenesis/experiments/L1_field/x140_sep0_s602.compact.json) | other | 596257 | `cf6d18c5b2a4433fc9370abe333b18a1c04c763f11b101b01df1a962276720e4` |
| [`morphogenesis/experiments/L1_field/x140_sep0_s603.compact.json`](../morphogenesis/experiments/L1_field/x140_sep0_s603.compact.json) | other | 558864 | `be70a23deea950bb7b342bff4827bcac2158a8c883447d6acfd631710a01491a` |
| [`morphogenesis/experiments/L1_field/x140_sep0_s604.compact.json`](../morphogenesis/experiments/L1_field/x140_sep0_s604.compact.json) | other | 517200 | `f26b72c2514d2dc95c461640fe9f5999f8f0657877025e1a688e5cec52858529` |
| [`morphogenesis/experiments/L1_field/x140_sep0_s605.compact.json`](../morphogenesis/experiments/L1_field/x140_sep0_s605.compact.json) | other | 517047 | `f5b0915627e3135f1b7ff6ffe7e3390fbb901cc46714ab01a361bad2e9bff9ea` |
| [`morphogenesis/experiments/L1_field/x140_sep16_s601.compact.json`](../morphogenesis/experiments/L1_field/x140_sep16_s601.compact.json) | other | 629353 | `8271cf80a92d5f71f3fdb77fd9b896d195f137c2941768f5f911fc3748efbcaf` |
| [`morphogenesis/experiments/L1_field/x140_sep16_s602.compact.json`](../morphogenesis/experiments/L1_field/x140_sep16_s602.compact.json) | other | 636567 | `0bd4ee1c2b2b58ab56fe8772e425d8ac0a34b3fe653348d75a1d1de89ec3c118` |
| [`morphogenesis/experiments/L1_field/x140_sep16_s603.compact.json`](../morphogenesis/experiments/L1_field/x140_sep16_s603.compact.json) | other | 610059 | `9a36740b941cfd5ff90886d297983519c74d785363107ff4b3a0e02dc19b53a9` |
| [`morphogenesis/experiments/L1_field/x140_sep16_s604.compact.json`](../morphogenesis/experiments/L1_field/x140_sep16_s604.compact.json) | other | 541889 | `74a63458a4ea409153e07413b59a185119459277186b933802e6d4592a261236` |
| [`morphogenesis/experiments/L1_field/x140_sep16_s605.compact.json`](../morphogenesis/experiments/L1_field/x140_sep16_s605.compact.json) | other | 541532 | `9bbedccb675749a205067b0c11a0c07c29de9c8e6a87c33a42b113f7375052c8` |
| [`morphogenesis/experiments/L1_field/x140_sep18_s601.compact.json`](../morphogenesis/experiments/L1_field/x140_sep18_s601.compact.json) | other | 614572 | `59ce1799744a168274d1c45b54f3cf6e67eb9e2212f64f67535267e625366f48` |
| [`morphogenesis/experiments/L1_field/x140_sep18_s602.compact.json`](../morphogenesis/experiments/L1_field/x140_sep18_s602.compact.json) | other | 575603 | `7c574c9070e87ad3801b7bb3a6574100a1a60fba764bfd9b2c09867ad9d666ce` |
| [`morphogenesis/experiments/L1_field/x140_sep18_s603.compact.json`](../morphogenesis/experiments/L1_field/x140_sep18_s603.compact.json) | other | 545365 | `899742d25aa1c4adf69b06931d6f9a42c2cfa99e9e1fa37ea8cacaa7ce804466` |
| [`morphogenesis/experiments/L1_field/x140_sep18_s604.compact.json`](../morphogenesis/experiments/L1_field/x140_sep18_s604.compact.json) | other | 563708 | `593324bda94b45045885dd32fbe52605a472cdff099b10e6f03a910001c9c318` |
| [`morphogenesis/experiments/L1_field/x140_sep18_s605.compact.json`](../morphogenesis/experiments/L1_field/x140_sep18_s605.compact.json) | other | 562672 | `84944d64692ba4f70467ef49a2097b856ee703757cb9f515867a6711aeeb03ba` |
| [`morphogenesis/experiments/L1_field/x140_sep20_s601.compact.json`](../morphogenesis/experiments/L1_field/x140_sep20_s601.compact.json) | other | 560241 | `584f9d5d67bd6ea952174aa04bf2be8c476415ef714c2ccbb42c441a96ee0975` |
| [`morphogenesis/experiments/L1_field/x140_sep20_s602.compact.json`](../morphogenesis/experiments/L1_field/x140_sep20_s602.compact.json) | other | 607750 | `b7d90b65f3bba071d970b3b562cec12585f178c1abf7af4fcd0e8ee22b0bef9d` |
| [`morphogenesis/experiments/L1_field/x140_sep20_s603.compact.json`](../morphogenesis/experiments/L1_field/x140_sep20_s603.compact.json) | other | 633544 | `502aa28a72940ce7e5baa76f6b1b7151ba821c37ed23df0faa1d99b8cb17fa86` |
| [`morphogenesis/experiments/L1_field/x140_sep20_s604.compact.json`](../morphogenesis/experiments/L1_field/x140_sep20_s604.compact.json) | other | 567822 | `e04ea22ae81f87e60cafe1f8244dfab47f3b5fafd2b8f98666f36a736c35e729` |
| [`morphogenesis/experiments/L1_field/x140_sep20_s605.compact.json`](../morphogenesis/experiments/L1_field/x140_sep20_s605.compact.json) | other | 568399 | `fcca4c853763d8fb8966fa053f281044f0b06ff5cec161d9e95ed8bef5c27121` |
| [`morphogenesis/experiments/L1_field/x140_sep22_s601.compact.json`](../morphogenesis/experiments/L1_field/x140_sep22_s601.compact.json) | other | 584018 | `54876c1720e025a418ca81130596cf312de8edc482be023f563ff6535a719f00` |
| [`morphogenesis/experiments/L1_field/x140_sep22_s602.compact.json`](../morphogenesis/experiments/L1_field/x140_sep22_s602.compact.json) | other | 586639 | `fcbee8e21e5543405af60b42e747bd68c3fc18e31d1d672b92e5f93f19531f75` |
| [`morphogenesis/experiments/L1_field/x140_sep22_s603.compact.json`](../morphogenesis/experiments/L1_field/x140_sep22_s603.compact.json) | other | 583227 | `9170d5098b5db33a4d33440a8762efc079ab719e0ec6f64a56157fc1a3b85339` |
| [`morphogenesis/experiments/L1_field/x140_sep22_s604.compact.json`](../morphogenesis/experiments/L1_field/x140_sep22_s604.compact.json) | other | 582458 | `0f3102d310195e4c18583174c139e3d30336ff90be75af150837f2b333754cac` |
| [`morphogenesis/experiments/L1_field/x140_sep22_s605.compact.json`](../morphogenesis/experiments/L1_field/x140_sep22_s605.compact.json) | other | 584521 | `9c02da5f960a9ad512e7074249ea2301641602f1cd65f7eb7847ee8f46024903` |
| [`morphogenesis/experiments/L1_field/x142_g3_r30_s601.compact.json`](../morphogenesis/experiments/L1_field/x142_g3_r30_s601.compact.json) | other | 548094 | `baf1ea10053fb2517f863b11b3c9afff408d3c7752cde9d976d0d8cf0dfd0b65` |
| [`morphogenesis/experiments/L1_field/x142_g3_r30_s602.compact.json`](../morphogenesis/experiments/L1_field/x142_g3_r30_s602.compact.json) | other | 546617 | `d7841932bd8fc6fa02cfb2f8b54eedab319cedee671132eff4713d0fd4b03689` |
| [`morphogenesis/experiments/L1_field/x142_g3_r30_s603.compact.json`](../morphogenesis/experiments/L1_field/x142_g3_r30_s603.compact.json) | other | 593265 | `11c4ff53b798beccdc79056bc0a500b3c3451276a6c9595370bca4475da6e720` |
| [`morphogenesis/experiments/L1_field/x142_g3_r30_s604.compact.json`](../morphogenesis/experiments/L1_field/x142_g3_r30_s604.compact.json) | other | 545216 | `dffbd590a3f30464bf28c5a94e73cf0ed902140f8a42ce0d2a4944629af026a6` |
| [`morphogenesis/experiments/L1_field/x142_g3_r30_s605.compact.json`](../morphogenesis/experiments/L1_field/x142_g3_r30_s605.compact.json) | other | 544109 | `ea4b19cab0c3609aada9ec214687fec87ae2e3e13197bb7f97c11325b436ee73` |
| [`morphogenesis/experiments/L1_field/x142_g4_r45_s601.compact.json`](../morphogenesis/experiments/L1_field/x142_g4_r45_s601.compact.json) | other | 547976 | `797445ce3afc25c559c3149b926f0e309664e365776aea29e62cb8c2e2976c7e` |
| [`morphogenesis/experiments/L1_field/x142_g4_r45_s602.compact.json`](../morphogenesis/experiments/L1_field/x142_g4_r45_s602.compact.json) | other | 543475 | `85facbe083499b807b8a40035318383edc6aeee2f13b552b895e743fec668978` |
| [`morphogenesis/experiments/L1_field/x142_g4_r45_s603.compact.json`](../morphogenesis/experiments/L1_field/x142_g4_r45_s603.compact.json) | other | 584942 | `7b3b6d6f55f71120bcf86cf1a8df669b447f458621e876a3dd2897e43827ae22` |
| [`morphogenesis/experiments/L1_field/x142_g4_r45_s604.compact.json`](../morphogenesis/experiments/L1_field/x142_g4_r45_s604.compact.json) | other | 535697 | `625d941e71beb04925b5ca3b90a5ff6afef60525411ceaa546ebf131d07d3f95` |
| [`morphogenesis/experiments/L1_field/x142_g4_r45_s605.compact.json`](../morphogenesis/experiments/L1_field/x142_g4_r45_s605.compact.json) | other | 534242 | `fef7585f2d610017b13e968d814752489b7d7d6fdd0d7287e1996bf3f1378974` |
| [`morphogenesis/experiments/L1_field/x142_g5_r45_s601.compact.json`](../morphogenesis/experiments/L1_field/x142_g5_r45_s601.compact.json) | other | 543996 | `b2bcdffa681cd2f6e092a8d020d53a3394b86d94108466760c9e48a4e1f3744d` |
| [`morphogenesis/experiments/L1_field/x142_g5_r45_s602.compact.json`](../morphogenesis/experiments/L1_field/x142_g5_r45_s602.compact.json) | other | 550439 | `9bf7ec4193849643ee57281b36d42029858713126aee2ec0d7fc56c6763e148e` |
| [`morphogenesis/experiments/L1_field/x142_g5_r45_s603.compact.json`](../morphogenesis/experiments/L1_field/x142_g5_r45_s603.compact.json) | other | 529003 | `5327f08eddbe83d6cf2cd701cec92ff232df813a9d456447f8bc8593d6be8da9` |
| [`morphogenesis/experiments/L1_field/x142_g5_r45_s604.compact.json`](../morphogenesis/experiments/L1_field/x142_g5_r45_s604.compact.json) | other | 584355 | `d7bca8c68778a092e383c32f8a0f967df743784b1e4873bc1991264106726068` |
| [`morphogenesis/experiments/L1_field/x142_g5_r45_s605.compact.json`](../morphogenesis/experiments/L1_field/x142_g5_r45_s605.compact.json) | other | 583876 | `f60b467809c416168296765f1c89ed8a06b8e012d798a57127852a1f4651f1b7` |
| [`morphogenesis/experiments/L1_field/x142_g6_r30_s601.compact.json`](../morphogenesis/experiments/L1_field/x142_g6_r30_s601.compact.json) | other | 529614 | `9f385893b70bc1365fc318e21821ce33fa6f2b5c39aab44127582009e898f8cc` |
| [`morphogenesis/experiments/L1_field/x142_g6_r30_s602.compact.json`](../morphogenesis/experiments/L1_field/x142_g6_r30_s602.compact.json) | other | 529157 | `ce6f4bc21a83ea41e16ad8460dcf7969fbc319e95eef180db606075fc74c4379` |
| [`morphogenesis/experiments/L1_field/x142_g6_r30_s603.compact.json`](../morphogenesis/experiments/L1_field/x142_g6_r30_s603.compact.json) | other | 562186 | `8a24f85e36caf6aeb60b5cd579d8f8ed404339676eda36229114ebc2742975f9` |
| [`morphogenesis/experiments/L1_field/x142_g6_r30_s604.compact.json`](../morphogenesis/experiments/L1_field/x142_g6_r30_s604.compact.json) | other | 512190 | `8815b076f5fbfa1717eb9aa12dc8a343f4fd549332862cced8f9d6847512e0f1` |
| [`morphogenesis/experiments/L1_field/x142_g6_r30_s605.compact.json`](../morphogenesis/experiments/L1_field/x142_g6_r30_s605.compact.json) | other | 512374 | `45e518784481191fdfbac8838f3bca1e2acd65d9bc24e3735bcd1c19b969828f` |
| [`morphogenesis/experiments/L1_field/x142_g6_r45_s601.compact.json`](../morphogenesis/experiments/L1_field/x142_g6_r45_s601.compact.json) | other | 468356 | `87404306490e9fb098ad00911099729c88773ee208397470185fa1a17a768e54` |
| [`morphogenesis/experiments/L1_field/x142_g6_r45_s602.compact.json`](../morphogenesis/experiments/L1_field/x142_g6_r45_s602.compact.json) | other | 576843 | `5b21cf7e23016b39b7f8b9c13fe2947c8ffc5094d3769aec0332b2218b10eac2` |
| [`morphogenesis/experiments/L1_field/x142_g6_r45_s603.compact.json`](../morphogenesis/experiments/L1_field/x142_g6_r45_s603.compact.json) | other | 557296 | `89d3c49e7f8abca38ba00e16e3ff5b1a288ef4c4e6b1cb240558b1642b3c915a` |
| [`morphogenesis/experiments/L1_field/x142_g6_r45_s604.compact.json`](../morphogenesis/experiments/L1_field/x142_g6_r45_s604.compact.json) | other | 564916 | `7896505adb0d0db28577cd10905d5f90924ff1b937f30d0642dfd96198c1373f` |
| [`morphogenesis/experiments/L1_field/x142_g6_r45_s605.compact.json`](../morphogenesis/experiments/L1_field/x142_g6_r45_s605.compact.json) | other | 563066 | `20294530eb6734d5521e51484faab885c2c78d9f2b29073e0659451abf9f22d3` |
| [`morphogenesis/experiments/L1_field/x142_g7_r30_s601.compact.json`](../morphogenesis/experiments/L1_field/x142_g7_r30_s601.compact.json) | other | 541997 | `d74dfab271bd49ba41933b94acb23d388d72ddc65e2c1b534e00bd93bd03d1bc` |
| [`morphogenesis/experiments/L1_field/x142_g7_r30_s602.compact.json`](../morphogenesis/experiments/L1_field/x142_g7_r30_s602.compact.json) | other | 522526 | `3b03ff1f0818249a40c096a7c5f107a8f18851486d4cbc19bb951ee11e129966` |
| [`morphogenesis/experiments/L1_field/x142_g7_r30_s603.compact.json`](../morphogenesis/experiments/L1_field/x142_g7_r30_s603.compact.json) | other | 531172 | `b8a2e059ac89b4f984a516232245b5df0e4ba9fbe659afc58ecc4067a211a191` |
| [`morphogenesis/experiments/L1_field/x142_g7_r30_s604.compact.json`](../morphogenesis/experiments/L1_field/x142_g7_r30_s604.compact.json) | other | 549991 | `f5d0264d3a3b456073b2832ccf39c0d0cdac671278b3f94fb19457519f961e92` |
| [`morphogenesis/experiments/L1_field/x142_g7_r30_s605.compact.json`](../morphogenesis/experiments/L1_field/x142_g7_r30_s605.compact.json) | other | 549490 | `30c0b19e012e27b04b95f1058c51d13aa71c2076128b01aa813bae6247054058` |
| [`morphogenesis/experiments/L1_field/x142_g9_r30_s601.compact.json`](../morphogenesis/experiments/L1_field/x142_g9_r30_s601.compact.json) | other | 565706 | `7ffa57c6fecb3e5a5638db3a971292bb5f3d12a3a53224f840d7b44be37ca61a` |
| [`morphogenesis/experiments/L1_field/x142_g9_r30_s602.compact.json`](../morphogenesis/experiments/L1_field/x142_g9_r30_s602.compact.json) | other | 496636 | `810212da08d0ff4b76cdfb6512026e63bc048af75c1dba6ce18a9b811533c007` |
| [`morphogenesis/experiments/L1_field/x142_g9_r30_s603.compact.json`](../morphogenesis/experiments/L1_field/x142_g9_r30_s603.compact.json) | other | 581693 | `d3c89f44813b6a69422d588def39a1228ff3e16d5ecc723af16e4c332b4ed9c3` |
| [`morphogenesis/experiments/L1_field/x142_g9_r30_s604.compact.json`](../morphogenesis/experiments/L1_field/x142_g9_r30_s604.compact.json) | other | 603019 | `647332ed8f90479be6ec2c260fe9a1b91ab7756aaaf727550e81bd9ed724defb` |
| [`morphogenesis/experiments/L1_field/x142_g9_r30_s605.compact.json`](../morphogenesis/experiments/L1_field/x142_g9_r30_s605.compact.json) | other | 604500 | `a8a4b82012d77a773b778fc37e793f5768f1b6afaf5ff89c1d934e6ce345ec7f` |
| [`morphogenesis/experiments/L1_field/x145_lone_r30_s601.compact.json`](../morphogenesis/experiments/L1_field/x145_lone_r30_s601.compact.json) | other | 421457 | `5bcbe395fa193c2d06006995e15786d51b46eacee9f23424eb57cb7708a58467` |
| [`morphogenesis/experiments/L1_field/x145_lone_r30_s602.compact.json`](../morphogenesis/experiments/L1_field/x145_lone_r30_s602.compact.json) | other | 524268 | `a875a269dc74928a3da6faade94bdb22a059b00544cafd9d51e58071765393ca` |
| [`morphogenesis/experiments/L1_field/x145_lone_r30_s603.compact.json`](../morphogenesis/experiments/L1_field/x145_lone_r30_s603.compact.json) | other | 523506 | `1e0a1a3a68aad31a1129bf34f8c69b4fcf9ad54454cf8b747ea58084a198b744` |
| [`morphogenesis/experiments/L1_field/x145_lone_r30_s604.compact.json`](../morphogenesis/experiments/L1_field/x145_lone_r30_s604.compact.json) | other | 528814 | `98b059087a151546f09637e0442e4ef2f005fd69e1484d32708bee6e8f02bda5` |
| [`morphogenesis/experiments/L1_field/x145_lone_r30_s605.compact.json`](../morphogenesis/experiments/L1_field/x145_lone_r30_s605.compact.json) | other | 529483 | `e1d69b74127d145fd66276d6f1bd050d8dc1f7151ca24e57f0c64d74bf9a98b0` |
| [`morphogenesis/experiments/L1_field/x147_g8_r45_s601.compact.json`](../morphogenesis/experiments/L1_field/x147_g8_r45_s601.compact.json) | other | 562357 | `f02b71959e96cef7e539604d5e357c67bc63f8339142d00e420f01d38b0ca95f` |
| [`morphogenesis/experiments/L1_field/x147_g8_r45_s602.compact.json`](../morphogenesis/experiments/L1_field/x147_g8_r45_s602.compact.json) | other | 551387 | `3ca055273b5a2944ba1cf01a821609f55f9ec00a66b0d0979c349089b5555461` |
| [`morphogenesis/experiments/L1_field/x147_g8_r45_s603.compact.json`](../morphogenesis/experiments/L1_field/x147_g8_r45_s603.compact.json) | other | 517071 | `dba12bbf5dbc9e407621e28c5a02b808faecf5e6a72ee55b65e7c4adc7bc525b` |
| [`morphogenesis/experiments/L1_field/x147_g8_r45_s604.compact.json`](../morphogenesis/experiments/L1_field/x147_g8_r45_s604.compact.json) | other | 563419 | `2d830e0827414c9b8a2fd10067fba8a5856c24df800a33a979620008262ce795` |
| [`morphogenesis/experiments/L1_field/x147_g8_r45_s605.compact.json`](../morphogenesis/experiments/L1_field/x147_g8_r45_s605.compact.json) | other | 561948 | `922beb222cdd542860b612b65140efa835ae674361ee12eb45c0b9501ed32c57` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s171.json`](../morphogenesis/experiments/L1_field/x14_p3000_s171.json) | other | 4738 | `0497617e24a4b53103606a70a2cc0805a627dc00a5695e943a37c9bfcbb35bb2` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s172.json`](../morphogenesis/experiments/L1_field/x14_p3000_s172.json) | other | 4581 | `7633deba087d4f21bc8991ab4c0b7a044a2456a0fe385f4af5cf1e4c91c6eac4` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s173.json`](../morphogenesis/experiments/L1_field/x14_p3000_s173.json) | other | 4408 | `9f3cb91bfce0c7bdbbc3fc29b88258f39d74e17ca6d1528f8e7455b67c4e48ff` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s174.json`](../morphogenesis/experiments/L1_field/x14_p3000_s174.json) | other | 4832 | `f2f9042767b52b05b96772d9af7f2271762a757fa8c216fcc10e8e61bb14ecda` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s175.json`](../morphogenesis/experiments/L1_field/x14_p3000_s175.json) | other | 4372 | `4e86430f06685212e376fa6d8b1aa9ec27b95b2f38bb0fb513613b9d0f0d04ef` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s176.json`](../morphogenesis/experiments/L1_field/x14_p3000_s176.json) | other | 4832 | `a25e716ec8065929abb721a4030a65f3071e0dc0b942ad5dbebc45fe7b5172ec` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s177.json`](../morphogenesis/experiments/L1_field/x14_p3000_s177.json) | other | 4473 | `0ab3fed99e61773dcffe98f6b23024d059cbea8af593f51882e8dc94e69c33a9` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s178.json`](../morphogenesis/experiments/L1_field/x14_p3000_s178.json) | other | 4429 | `51d216788cb5ca4d7a3db1528e99e90eb530ba0bea3924cbbcec110f62229553` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s179.json`](../morphogenesis/experiments/L1_field/x14_p3000_s179.json) | other | 4545 | `d184f6c9f410f9e0ccef25f6f962b54b08fc4375fb373efbf8e4cb8402dbd818` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s180.json`](../morphogenesis/experiments/L1_field/x14_p3000_s180.json) | other | 4610 | `d54c59d9c098dca636d0b9df8a4b1dea1f87d6eeb84de586b45f41d637c98fbb` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s181.json`](../morphogenesis/experiments/L1_field/x14_p3000_s181.json) | other | 4381 | `b2488576dfa1c628367218cb43b980491f8251749e6dc0036c243e288d1a12cc` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s182.json`](../morphogenesis/experiments/L1_field/x14_p3000_s182.json) | other | 4235 | `54fa0cda21a0bb1e02420959e266eaf623bc2f948e73058e43c4aa7456303cc7` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s183.json`](../morphogenesis/experiments/L1_field/x14_p3000_s183.json) | other | 4326 | `543e3f9f87c54b1368a0cb079b78c630340eefe3741e04c590ca187fa83e4605` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s184.json`](../morphogenesis/experiments/L1_field/x14_p3000_s184.json) | other | 4569 | `eb7c56045542cdbbd3829c7b78b2fe93775905ce5c07ec740f7d2786ae85b73e` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s185.json`](../morphogenesis/experiments/L1_field/x14_p3000_s185.json) | other | 5263 | `f749c27fa995e2ccf86f9bf609b5543a6eec2de7843b8ce3cf1f900df38d985d` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s186.json`](../morphogenesis/experiments/L1_field/x14_p3000_s186.json) | other | 4649 | `17706e3365acc3a0d4649387cde24f807a054c2ae7587f7526a8e97bddfa53fb` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s187.json`](../morphogenesis/experiments/L1_field/x14_p3000_s187.json) | other | 4384 | `6c8b1f2a9187a745b3d904548c6630bc410cadffa68446c396069ae5938527de` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s188.json`](../morphogenesis/experiments/L1_field/x14_p3000_s188.json) | other | 4099 | `5900c2b5ddec5f89a45218d3312e90741521c44da6c5ba19c1813e9b6db86d05` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s189.json`](../morphogenesis/experiments/L1_field/x14_p3000_s189.json) | other | 4348 | `5f47851c58a614988d8ea31c984dab2ae93fee4b94403cdbce5a5c6fec35564d` |
| [`morphogenesis/experiments/L1_field/x14_p3000_s190.json`](../morphogenesis/experiments/L1_field/x14_p3000_s190.json) | other | 4912 | `8413f15fb5ba9db4f545d30cca5ef88b04de8c299b9c8553be762e6302ba38ad` |
| [`morphogenesis/experiments/L1_field/x150_g6_r60_s601.compact.json`](../morphogenesis/experiments/L1_field/x150_g6_r60_s601.compact.json) | other | 518899 | `5e1712d1118cc46b5db6a9932ddcea3821859149c2b6bf3cb9e72e418b8e2611` |
| [`morphogenesis/experiments/L1_field/x150_g6_r60_s602.compact.json`](../morphogenesis/experiments/L1_field/x150_g6_r60_s602.compact.json) | other | 598757 | `2a6faa38d004ecb4abdb4377ad24c2d64c317b0d5809274e95d7ce01f71793ad` |
| [`morphogenesis/experiments/L1_field/x150_g6_r60_s603.compact.json`](../morphogenesis/experiments/L1_field/x150_g6_r60_s603.compact.json) | other | 556531 | `175437fd2fe0952ade1f02ce870afc2eef159d4fcc787cc0a51fc95360556d51` |
| [`morphogenesis/experiments/L1_field/x150_g6_r60_s604.compact.json`](../morphogenesis/experiments/L1_field/x150_g6_r60_s604.compact.json) | other | 536930 | `a9f6e4856a68fcee221e7cbfc66f67b0acd5094b2a1caa59d48c24279bd3c5f8` |
| [`morphogenesis/experiments/L1_field/x150_g6_r60_s605.compact.json`](../morphogenesis/experiments/L1_field/x150_g6_r60_s605.compact.json) | other | 537441 | `de25ae9e5ab2e788da630e8714c0f2731419d59236e46ae59264a32c3f03ac33` |
| [`morphogenesis/experiments/L1_field/x150_g7_r60_s601.compact.json`](../morphogenesis/experiments/L1_field/x150_g7_r60_s601.compact.json) | other | 475442 | `2cd3f2f5e0061d289a5486330cde4ee1634f9f1fe5708d7c8d3ac96c3d08a3ff` |
| [`morphogenesis/experiments/L1_field/x150_g7_r60_s602.compact.json`](../morphogenesis/experiments/L1_field/x150_g7_r60_s602.compact.json) | other | 570065 | `b299979eac0e6acad0333dce3e3db6b8931091e808b0c0fc1fd85bdfb2faa027` |
| [`morphogenesis/experiments/L1_field/x150_g7_r60_s603.compact.json`](../morphogenesis/experiments/L1_field/x150_g7_r60_s603.compact.json) | other | 592580 | `004a336e24cca852f4643b0e91be563784b5670227e0c9dd85a6e09991288525` |
| [`morphogenesis/experiments/L1_field/x150_g7_r60_s604.compact.json`](../morphogenesis/experiments/L1_field/x150_g7_r60_s604.compact.json) | other | 538865 | `234adeae55e6893e59d803d2e29f6405f7cc7e8511f6cb79e961147ee1bddf4e` |
| [`morphogenesis/experiments/L1_field/x150_g7_r60_s605.compact.json`](../morphogenesis/experiments/L1_field/x150_g7_r60_s605.compact.json) | other | 538444 | `cdbe75fa190c27e9d957ad1235cc7df9c4e4c03c5706d6e8168492072c6d266a` |
| [`morphogenesis/experiments/L1_field/x150_g8_r60_s601.compact.json`](../morphogenesis/experiments/L1_field/x150_g8_r60_s601.compact.json) | other | 607347 | `3fdee89f9f1eac1fd47ae2c2d0b64facd44b79976d43cb629427c365b88b492d` |
| [`morphogenesis/experiments/L1_field/x150_g8_r60_s602.compact.json`](../morphogenesis/experiments/L1_field/x150_g8_r60_s602.compact.json) | other | 608966 | `0a1fd23d26cf7e787dc82dbffab914304bdb77c0f49417a242a22678ccafbc2f` |
| [`morphogenesis/experiments/L1_field/x150_g8_r60_s603.compact.json`](../morphogenesis/experiments/L1_field/x150_g8_r60_s603.compact.json) | other | 614116 | `dc7df14d4ddc3332747eb943c7f9f6cb1ec309f5680b1e96819d9aba0c44f146` |
| [`morphogenesis/experiments/L1_field/x150_g8_r60_s604.compact.json`](../morphogenesis/experiments/L1_field/x150_g8_r60_s604.compact.json) | other | 573144 | `a2813360cd9dbb7b8cc36cf02c6a3bbac9ff0adfc6a2a68ed0aa897e77c676e4` |
| [`morphogenesis/experiments/L1_field/x150_g8_r60_s605.compact.json`](../morphogenesis/experiments/L1_field/x150_g8_r60_s605.compact.json) | other | 573192 | `7201df812034afb0ab7523cea7b920c9d37053fdac285b47ff53fdc324a4e270` |
| [`morphogenesis/experiments/L1_field/x151_g7_r525_s601.compact.json`](../morphogenesis/experiments/L1_field/x151_g7_r525_s601.compact.json) | other | 589866 | `5b6f992ddc93fd77da775b28dbea49a7e1b66c638c5e3913d100d1eac7a0786f` |
| [`morphogenesis/experiments/L1_field/x151_g7_r525_s602.compact.json`](../morphogenesis/experiments/L1_field/x151_g7_r525_s602.compact.json) | other | 552969 | `4988bdae60697cb03a203421fe368343cbadd17b49ccd63c04b29826dd6d6d84` |
| [`morphogenesis/experiments/L1_field/x151_g7_r525_s603.compact.json`](../morphogenesis/experiments/L1_field/x151_g7_r525_s603.compact.json) | other | 544266 | `21589d3dfe0985a819f14b9878b7cdcd02ad98660935d9cfc9b74b6e2f6f1029` |
| [`morphogenesis/experiments/L1_field/x151_g7_r525_s604.compact.json`](../morphogenesis/experiments/L1_field/x151_g7_r525_s604.compact.json) | other | 586215 | `87a79679077175e7704fdde1736fe11cd4fc8f7186a0baf517c5e0ffd67713e6` |
| [`morphogenesis/experiments/L1_field/x151_g7_r525_s605.compact.json`](../morphogenesis/experiments/L1_field/x151_g7_r525_s605.compact.json) | other | 587389 | `7d238efb2b70ac68376c7d3e0155bafcee97f1da4bcb4c6bd79010d2be8f4d36` |
| [`morphogenesis/experiments/L1_field/x151_g8_r525_s601.compact.json`](../morphogenesis/experiments/L1_field/x151_g8_r525_s601.compact.json) | other | 539333 | `2c4bcc67b3f24d17afb01d206e91f202c4337a03a966c0da635f5f0e7e106dcb` |
| [`morphogenesis/experiments/L1_field/x151_g8_r525_s602.compact.json`](../morphogenesis/experiments/L1_field/x151_g8_r525_s602.compact.json) | other | 582180 | `8a1d78a4240b4d8c4eb51a628f21439fc2aea711c6b6f70dd3821232e166662f` |
| [`morphogenesis/experiments/L1_field/x151_g8_r525_s603.compact.json`](../morphogenesis/experiments/L1_field/x151_g8_r525_s603.compact.json) | other | 531358 | `bbd169ec1bb95d2bf7b7e7f0af0d0cddef9ee81d9339ac5b256088b3af4b5574` |
| [`morphogenesis/experiments/L1_field/x151_g8_r525_s604.compact.json`](../morphogenesis/experiments/L1_field/x151_g8_r525_s604.compact.json) | other | 566975 | `c796992a892c1f696eae45ee97bc7cbe8309ed2f10b0fc911c6015fd07ff0852` |
| [`morphogenesis/experiments/L1_field/x151_g8_r525_s605.compact.json`](../morphogenesis/experiments/L1_field/x151_g8_r525_s605.compact.json) | other | 566143 | `4c7215c356ea35170cb43d2693ce3d4e6f80ae6f8213671203ca113416abce6a` |
| [`morphogenesis/experiments/L1_field/x153_g75_r60_s601.compact.json`](../morphogenesis/experiments/L1_field/x153_g75_r60_s601.compact.json) | other | 630853 | `5f4cfe8dfcf44241c8a11d99a244c56784c16525735907afaa1d33e5db6524e2` |
| [`morphogenesis/experiments/L1_field/x153_g75_r60_s602.compact.json`](../morphogenesis/experiments/L1_field/x153_g75_r60_s602.compact.json) | other | 553194 | `7385517583ba55494683659480239c4f895a25f2ca69249015e7afec84c53eef` |
| [`morphogenesis/experiments/L1_field/x153_g75_r60_s603.compact.json`](../morphogenesis/experiments/L1_field/x153_g75_r60_s603.compact.json) | other | 615957 | `41bef9d067cd9274cfe0fa63571eef866687826e8f3ed7705b029ee76b8fea17` |
| [`morphogenesis/experiments/L1_field/x153_g75_r60_s604.compact.json`](../morphogenesis/experiments/L1_field/x153_g75_r60_s604.compact.json) | other | 573616 | `97642637fc60f750d25a95ecec7f44777f266ea6a7f28540fcdf098c194cd912` |
| [`morphogenesis/experiments/L1_field/x153_g75_r60_s605.compact.json`](../morphogenesis/experiments/L1_field/x153_g75_r60_s605.compact.json) | other | 571550 | `2bb914da0f09586ea1bb38feeb4d7b5d662ad449b556c6b9af14161098861631` |
| [`morphogenesis/experiments/L1_field/x153_g75_r60_s606.compact.json`](../morphogenesis/experiments/L1_field/x153_g75_r60_s606.compact.json) | other | 547416 | `1901450cc86915c8e6bf1cb5a21f5210a7f04439015a877415716b3beb974201` |
| [`morphogenesis/experiments/L1_field/x153_g75_r60_s607.compact.json`](../morphogenesis/experiments/L1_field/x153_g75_r60_s607.compact.json) | other | 578456 | `8221b8b4097ff369ae42c27a61535828dba03debeeb611cbb9d7b7261896a34c` |
| [`morphogenesis/experiments/L1_field/x153_g75_r60_s608.compact.json`](../morphogenesis/experiments/L1_field/x153_g75_r60_s608.compact.json) | other | 511829 | `e5c7dff1f4bd9f5a273ef3b0fc7550736f90b323adbc46845e8f1fd9f00bcb1c` |
| [`morphogenesis/experiments/L1_field/x153_g75_r60_s609.compact.json`](../morphogenesis/experiments/L1_field/x153_g75_r60_s609.compact.json) | other | 618605 | `f24c9eb0fdac7bf8b2b4b3fa753e4bcacdc0cfb7f70cf4041c11ff9fcb0d8aba` |
| [`morphogenesis/experiments/L1_field/x153_g75_r60_s610.compact.json`](../morphogenesis/experiments/L1_field/x153_g75_r60_s610.compact.json) | other | 560378 | `32f31865ec5f4ff133cbe9e1ab88499c7817be3fa3a16fbe384073af27c6efbd` |
| [`morphogenesis/experiments/L1_field/x154_g65_r60_s601.compact.json`](../morphogenesis/experiments/L1_field/x154_g65_r60_s601.compact.json) | other | 470722 | `87a034c778ceda55a576444f40932bdd06ba7b9ec2632b3095d7f71ea7922eb8` |
| [`morphogenesis/experiments/L1_field/x154_g65_r60_s602.compact.json`](../morphogenesis/experiments/L1_field/x154_g65_r60_s602.compact.json) | other | 563833 | `b414caaef035fad77bf8222733a6a987d442a274f6c7c8be43d94884d07c27e0` |
| [`morphogenesis/experiments/L1_field/x154_g65_r60_s603.compact.json`](../morphogenesis/experiments/L1_field/x154_g65_r60_s603.compact.json) | other | 614888 | `23177768aba7e8061d023aa2e4639e591956782f984538a91b99e93750b03d59` |
| [`morphogenesis/experiments/L1_field/x154_g65_r60_s604.compact.json`](../morphogenesis/experiments/L1_field/x154_g65_r60_s604.compact.json) | other | 535463 | `3d9ef43bbec093f97088a6b309e20ca912546c42c3f924e57a3f6cc0017fa389` |
| [`morphogenesis/experiments/L1_field/x154_g65_r60_s605.compact.json`](../morphogenesis/experiments/L1_field/x154_g65_r60_s605.compact.json) | other | 537037 | `099c269310d5e83690a1e25a97e1459141897df9969e9d37edb4f723e7f0c8e7` |
| [`morphogenesis/experiments/L1_field/x154_g65_r60_s606.compact.json`](../morphogenesis/experiments/L1_field/x154_g65_r60_s606.compact.json) | other | 567432 | `2c4702096a83c5f94e90de306b3763689a15f846eafe4ece7476c699096912ef` |
| [`morphogenesis/experiments/L1_field/x154_g65_r60_s607.compact.json`](../morphogenesis/experiments/L1_field/x154_g65_r60_s607.compact.json) | other | 595837 | `70147e83af543fb6b9a5f9d421c406f163299bc6923fe8b8527f4372e242fc17` |
| [`morphogenesis/experiments/L1_field/x154_g65_r60_s608.compact.json`](../morphogenesis/experiments/L1_field/x154_g65_r60_s608.compact.json) | other | 545852 | `8430567052c5e862ef6cb03a50b21e34d4c7ff16b3934c288096a7fe2c96b306` |
| [`morphogenesis/experiments/L1_field/x154_g65_r60_s609.compact.json`](../morphogenesis/experiments/L1_field/x154_g65_r60_s609.compact.json) | other | 617143 | `b9f9ddb119c1be4f3034166553dbc7399fcc129675a5f2dcf31255e10d6871bc` |
| [`morphogenesis/experiments/L1_field/x154_g65_r60_s610.compact.json`](../morphogenesis/experiments/L1_field/x154_g65_r60_s610.compact.json) | other | 628926 | `d9cb48d4508ee2d767b8d5c402f0ba976bbece374fcf1d618ce46693374b891b` |
| [`morphogenesis/experiments/L1_field/x154_g70_r60_s606.compact.json`](../morphogenesis/experiments/L1_field/x154_g70_r60_s606.compact.json) | other | 546759 | `91f2c611c9efd88c1f0745ca0d60a2e8015c5759a9ea985daf454a95fb868242` |
| [`morphogenesis/experiments/L1_field/x154_g70_r60_s607.compact.json`](../morphogenesis/experiments/L1_field/x154_g70_r60_s607.compact.json) | other | 587440 | `6583316f1b818dfbf28d7f2f306092c075c96d4b16ceddd5757eba4d193c59cf` |
| [`morphogenesis/experiments/L1_field/x154_g70_r60_s608.compact.json`](../morphogenesis/experiments/L1_field/x154_g70_r60_s608.compact.json) | other | 569852 | `94baefdf2f532835c0645da792be5b219ddd98cbff75801d1bbe3ca4bd3209d9` |
| [`morphogenesis/experiments/L1_field/x154_g70_r60_s609.compact.json`](../morphogenesis/experiments/L1_field/x154_g70_r60_s609.compact.json) | other | 594073 | `aa9d9cfbe9a262d2179f6cbbf013ee1d992b1543948f0104e0d55bddda34d2a1` |
| [`morphogenesis/experiments/L1_field/x154_g70_r60_s610.compact.json`](../morphogenesis/experiments/L1_field/x154_g70_r60_s610.compact.json) | other | 592353 | `93e517f9347568d2c12bb49d2ff4b0ca16b4c1197b2d8991d9ca2f552d272853` |
| [`morphogenesis/experiments/L1_field/x154_g80_r60_s606.compact.json`](../morphogenesis/experiments/L1_field/x154_g80_r60_s606.compact.json) | other | 570238 | `7d6196a006ad3f05230a103bce9b7aeb3e731b10db234e9aeeb589d483311002` |
| [`morphogenesis/experiments/L1_field/x154_g80_r60_s607.compact.json`](../morphogenesis/experiments/L1_field/x154_g80_r60_s607.compact.json) | other | 554676 | `6730246c05a0c1f5149bb9eda727793fa5bb0b6445ed2eae922c912420ceb84e` |
| [`morphogenesis/experiments/L1_field/x154_g80_r60_s608.compact.json`](../morphogenesis/experiments/L1_field/x154_g80_r60_s608.compact.json) | other | 564169 | `f5ac336d84b54857db927680fc7db77c440bde79e9a15496f57a95fbec0a4aab` |
| [`morphogenesis/experiments/L1_field/x154_g80_r60_s609.compact.json`](../morphogenesis/experiments/L1_field/x154_g80_r60_s609.compact.json) | other | 615004 | `380a393687fcf25191cadb8fecd7fd5c8130496595b656eed5afe8fa226383be` |
| [`morphogenesis/experiments/L1_field/x154_g80_r60_s610.compact.json`](../morphogenesis/experiments/L1_field/x154_g80_r60_s610.compact.json) | other | 613419 | `cd9a75f2b58ce51da1d7e29341786a422410db05a24cf7cd83d39833a2777d90` |
| [`morphogenesis/experiments/L1_field/x154_series_index.json`](../morphogenesis/experiments/L1_field/x154_series_index.json) | other | 2730 | `f7bcf8e1581f262af54de7af376348b012bb973ec9f660f519e3c9ad47fe68f6` |
| [`morphogenesis/experiments/L1_field/x155_ablation_index.json`](../morphogenesis/experiments/L1_field/x155_ablation_index.json) | other | 549 | `6f78ec94beaebd534579e29c8e2c2c554d10af7cb4f67374d58d100b380ee4eb` |
| [`morphogenesis/experiments/L1_field/x155_anchor_f030_s301.json`](../morphogenesis/experiments/L1_field/x155_anchor_f030_s301.json) | other | 3726735 | `f4ba4d5e0c7f9e29209c892aed2956ec18cfb5d457b5e07348d35cd5e01ce8a6` |
| [`morphogenesis/experiments/L1_field/x155_nomut_f030_s301.json`](../morphogenesis/experiments/L1_field/x155_nomut_f030_s301.json) | other | 3650042 | `776db49bd11cd17774e79a26ee8fc05b85b82f4a58f9fcfa15c49bd120e15173` |
| [`morphogenesis/experiments/L1_field/x155_nomut_f030_s302.json`](../morphogenesis/experiments/L1_field/x155_nomut_f030_s302.json) | other | 4297515 | `c09698009e3862126cf5afcbd9fc7808295eb53ac7a29ef551ab9685b31c42d4` |
| [`morphogenesis/experiments/L1_field/x156_series_index.json`](../morphogenesis/experiments/L1_field/x156_series_index.json) | other | 3297 | `1873c6ec98ab1be4aeffc7c47bdbc21aef94d13e67f7a45489758991b4fd6034` |
| [`morphogenesis/experiments/L1_field/x156_shape_f030_s801.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f030_s801.compact.json) | other | 2077814 | `56ad4496a0988c5e491209f49cf9008fbe8c8e40ff07b6c2cf98d811789239a6` |
| [`morphogenesis/experiments/L1_field/x156_shape_f030_s802.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f030_s802.compact.json) | other | 1787085 | `03706b8bb4ab92236eff82233713b825aafed10e5707d1601f3f0344a8186d9f` |
| [`morphogenesis/experiments/L1_field/x156_shape_f030_s803.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f030_s803.compact.json) | other | 1716548 | `9d46164da9f028f5e23ada93cac079864c0583268f572c832130c79debbacc32` |
| [`morphogenesis/experiments/L1_field/x156_shape_f030_s804.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f030_s804.compact.json) | other | 1547737 | `6b5fc2d44c7c67ff4d39ab50a24a5419c340e0a17e093eb039479cdf33cb38bf` |
| [`morphogenesis/experiments/L1_field/x156_shape_f030_s805.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f030_s805.compact.json) | other | 1919154 | `68a56ccd7ea58d28fd8c804544ed766d86f64e6dee0084f875e588bfae00dfed` |
| [`morphogenesis/experiments/L1_field/x156_shape_f030_s806.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f030_s806.compact.json) | other | 1967835 | `cfad256892332e37cfcc51a7ffb81977ca3ac968e8e0142b71db75a8f79f7fe9` |
| [`morphogenesis/experiments/L1_field/x156_shape_f030_s807.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f030_s807.compact.json) | other | 2110350 | `feb20c57a9352772a57e28a46cb07e02d6774e0cff66b32a099e44dcbd5e4592` |
| [`morphogenesis/experiments/L1_field/x156_shape_f030_s808.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f030_s808.compact.json) | other | 1857945 | `a17b9bf202ef019400253d6a3476b7a5d69a17a31627bc31195b17466a518478` |
| [`morphogenesis/experiments/L1_field/x156_shape_f030_s809.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f030_s809.compact.json) | other | 1959622 | `63631325447043e6cb068f746362b7d90193690c37bed72ad34471311bf28244` |
| [`morphogenesis/experiments/L1_field/x156_shape_f030_s810.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f030_s810.compact.json) | other | 2007801 | `499c5b66aa5d888a913bfbc3b3d03a5198758869f8aa5f817f0aacf33fb19e14` |
| [`morphogenesis/experiments/L1_field/x156_shape_f040_s801.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f040_s801.compact.json) | other | 332116 | `58bc48c420246abbdf5badd12d821fcced0aff2dc59660129b6d822f655632d7` |
| [`morphogenesis/experiments/L1_field/x156_shape_f040_s802.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f040_s802.compact.json) | other | 399966 | `f4571a2aa19c9fd508720f3db7069f06ecffbdd693d8e576022d31a9b661abb5` |
| [`morphogenesis/experiments/L1_field/x156_shape_f040_s803.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f040_s803.compact.json) | other | 264431 | `d8abe58b47540420f85a0da755506098a23ec070e0c542b65a230eaa1388b35a` |
| [`morphogenesis/experiments/L1_field/x156_shape_f040_s804.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f040_s804.compact.json) | other | 292940 | `3079ddbc8e6cfedefb5c22d10ff52493e9d023b1c9134033a430e6bec6f2a9ea` |
| [`morphogenesis/experiments/L1_field/x156_shape_f040_s805.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f040_s805.compact.json) | other | 246608 | `c615096644691a7da9023d6c1392ccd57e609971e8802a1211c9fc33b4a06773` |
| [`morphogenesis/experiments/L1_field/x156_shape_f040_s806.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f040_s806.compact.json) | other | 248258 | `1fb7c626e39fd0e47aa08d7bce26b037a26541cec064d8252f2cebd0c6c548ad` |
| [`morphogenesis/experiments/L1_field/x156_shape_f040_s807.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f040_s807.compact.json) | other | 514773 | `4ac45d0190f03023e90f0498507d6d64195cc19eb677b40484cf5a9e8ee5462c` |
| [`morphogenesis/experiments/L1_field/x156_shape_f040_s808.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f040_s808.compact.json) | other | 243130 | `41f766c79c8e2d62369dfadfc76947aa396b2788b59e840f630eff0f172fc7b2` |
| [`morphogenesis/experiments/L1_field/x156_shape_f040_s809.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f040_s809.compact.json) | other | 298472 | `4b86fd0876e8756334e15cf8496aab217b06caab6437f75dc9643e3714114c1c` |
| [`morphogenesis/experiments/L1_field/x156_shape_f040_s810.compact.json`](../morphogenesis/experiments/L1_field/x156_shape_f040_s810.compact.json) | other | 257245 | `3f5419132d24bf9420b06e4c60efd9f4df00910eb0ce55865ab749dd90dc4aaf` |
| [`morphogenesis/experiments/L1_field/x158_g10_r30_s701.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r30_s701.compact.json) | other | 587975 | `3407863c0a6101739209ce82b0c5b529a8539611b43b2bfc524efc40acc8033b` |
| [`morphogenesis/experiments/L1_field/x158_g10_r30_s702.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r30_s702.compact.json) | other | 560893 | `bfd7fb3a9fc27c3664a4be533151c1ed84c77f14bda746c41a9fb831a99c921b` |
| [`morphogenesis/experiments/L1_field/x158_g10_r30_s703.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r30_s703.compact.json) | other | 539075 | `08f1e0d90f68da1c62979757fb01feb5f0a24ac70566cfc249bd980793a878c2` |
| [`morphogenesis/experiments/L1_field/x158_g10_r30_s704.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r30_s704.compact.json) | other | 536073 | `691b2e4376940e26085f9f17d949e0114abfb66c6cdd8a10e60cb1c22d30de8c` |
| [`morphogenesis/experiments/L1_field/x158_g10_r30_s705.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r30_s705.compact.json) | other | 577430 | `a0c1eb862bebb8956e49c1cca1d649299ea74134b833a0ba8b7a14c4e2a71cd9` |
| [`morphogenesis/experiments/L1_field/x158_g10_r30_s706.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r30_s706.compact.json) | other | 573588 | `a4c3e9fb177885acdcc7e637c9d576475a4fb0e0ed99850cec01028e5446ec3f` |
| [`morphogenesis/experiments/L1_field/x158_g10_r30_s707.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r30_s707.compact.json) | other | 577392 | `0d510fb0d42354eb8f64cac8401dbec99e5472972c0f1b2ac315bf2726a6fcbe` |
| [`morphogenesis/experiments/L1_field/x158_g10_r30_s708.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r30_s708.compact.json) | other | 573730 | `8a13c473ba8a8add5db950b13cdbb8d29883d0cd2ff370acd67aecfb72adb7ae` |
| [`morphogenesis/experiments/L1_field/x158_g10_r30_s709.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r30_s709.compact.json) | other | 544665 | `5c61b8caf5653a414fe5f13e2bb5c94453eadcdbb596f50549603707aac45565` |
| [`morphogenesis/experiments/L1_field/x158_g10_r45_s701.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r45_s701.compact.json) | other | 544659 | `0f7ee5be9b585d29ca7ce842d765a783d2646a20217558b31cf0b83151662816` |
| [`morphogenesis/experiments/L1_field/x158_g10_r45_s702.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r45_s702.compact.json) | other | 543726 | `487f278e36b1fb0e2675bf149bf705b8b508fdd4e18114fd9463ec3124d33861` |
| [`morphogenesis/experiments/L1_field/x158_g10_r45_s703.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r45_s703.compact.json) | other | 548660 | `614ed70246087ece4391faa416160b1e4bd8dc4a1f1a4451eacbefc4bf4efb71` |
| [`morphogenesis/experiments/L1_field/x158_g10_r45_s704.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r45_s704.compact.json) | other | 555399 | `b3fbbef44a72aef3b72c4171440624ca8fcb76f21471155441dcd9bf4324b3b1` |
| [`morphogenesis/experiments/L1_field/x158_g10_r45_s705.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r45_s705.compact.json) | other | 544992 | `64afabffc7275b2299ee232296432b501135d38b8c63e421e5e811a32d329961` |
| [`morphogenesis/experiments/L1_field/x158_g10_r45_s706.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r45_s706.compact.json) | other | 601684 | `0a93b4dd9e79bab094f0013583b250d4822e9cac429fa8dfeee6c8d5ccb63d4a` |
| [`morphogenesis/experiments/L1_field/x158_g10_r45_s707.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r45_s707.compact.json) | other | 545614 | `3dbdde19eb8cbad90b2205b2f0faf34cdcdd74e082260c2588ca230a4b749508` |
| [`morphogenesis/experiments/L1_field/x158_g10_r45_s708.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r45_s708.compact.json) | other | 603475 | `3f8dd6ec03a6c84074cf885f14373e7b0f6295afb18007cfe6be7342889a9b7d` |
| [`morphogenesis/experiments/L1_field/x158_g10_r45_s709.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r45_s709.compact.json) | other | 567527 | `0c1b7543c04bc2e85040cdbcbe57fcff9f42bdd03b04f8b6d970c0cdbaa473a6` |
| [`morphogenesis/experiments/L1_field/x158_g10_r60_s701.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r60_s701.compact.json) | other | 567227 | `59ef18bd99981eed3b006c305f664640a4bcdcf89f5a761fbf5306dc10c8ed1b` |
| [`morphogenesis/experiments/L1_field/x158_g10_r60_s702.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r60_s702.compact.json) | other | 575527 | `d31ac407625436389bbb9cf3ca93492cef0097be243e3a3010c56558ddc7c867` |
| [`morphogenesis/experiments/L1_field/x158_g10_r60_s703.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r60_s703.compact.json) | other | 522126 | `e1438640dab2057a15d646eb43b46b2eab4cdf86e9b19312170e44cb92361524` |
| [`morphogenesis/experiments/L1_field/x158_g10_r60_s704.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r60_s704.compact.json) | other | 563440 | `aecccde64e24571eb616c175b61cc73ed692b24b762c73721d475fec2411db29` |
| [`morphogenesis/experiments/L1_field/x158_g10_r60_s705.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r60_s705.compact.json) | other | 566591 | `dd7fd55a6fbbc9c53f125c3a21211a7f57d92576525e7cacb6259e6d8970af04` |
| [`morphogenesis/experiments/L1_field/x158_g10_r60_s706.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r60_s706.compact.json) | other | 526934 | `861471bebf0e1510e8828785793b09d511be9dda3c1dddb41368ea30b1c68b68` |
| [`morphogenesis/experiments/L1_field/x158_g10_r60_s707.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r60_s707.compact.json) | other | 566123 | `2c3819a5c356f346f3af1cd457c223c8f55cec2f16082f6b8c35f80016e20acf` |
| [`morphogenesis/experiments/L1_field/x158_g10_r60_s708.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r60_s708.compact.json) | other | 525983 | `4f86f4e34ea9d39afdeca244fc9b7a33520c01d4d21c5c9b3b63303bc5d99d2b` |
| [`morphogenesis/experiments/L1_field/x158_g10_r60_s709.compact.json`](../morphogenesis/experiments/L1_field/x158_g10_r60_s709.compact.json) | other | 566718 | `ea5409f92c09ffd3c4e77b0d9cda4494913b6bc647fdad73c752c67f62f0023e` |
| [`morphogenesis/experiments/L1_field/x158_g11_r30_s701.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r30_s701.compact.json) | other | 567395 | `26bcac278297c1be2f7aee477ff8964c5e85c4709eb86309319c821197897086` |
| [`morphogenesis/experiments/L1_field/x158_g11_r30_s702.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r30_s702.compact.json) | other | 539191 | `55fd8ef3b0bbc2b790c5cb9c7d15a710230172ac5dac26b8d8b16dc7115c4363` |
| [`morphogenesis/experiments/L1_field/x158_g11_r30_s703.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r30_s703.compact.json) | other | 536585 | `cf18231bf43a613cb7629e535e44ecbe5668ab103e4bf2f56b354c8b90f297b0` |
| [`morphogenesis/experiments/L1_field/x158_g11_r30_s704.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r30_s704.compact.json) | other | 544838 | `e49e39354294f677fbfbb13625eb67b3a747c32adc8dca47c3047c30144e964a` |
| [`morphogenesis/experiments/L1_field/x158_g11_r30_s705.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r30_s705.compact.json) | other | 522539 | `7469ce1f527f15857954d440f5ddca86fca1e565f364f134119f1ebaac61c451` |
| [`morphogenesis/experiments/L1_field/x158_g11_r30_s706.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r30_s706.compact.json) | other | 528799 | `37a5bfa358ab54ee57da2414aa75e21ecb69732966ebd7709559f432e98f2d86` |
| [`morphogenesis/experiments/L1_field/x158_g11_r30_s707.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r30_s707.compact.json) | other | 523378 | `4e123be2656ff4e714e8808b91197b79cf73524f9acff4490d6cf27f0a906e06` |
| [`morphogenesis/experiments/L1_field/x158_g11_r30_s708.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r30_s708.compact.json) | other | 528382 | `eb54de349d70e6458f1353b8926235f871094cebf1b342ee2faab74aeb29ae65` |
| [`morphogenesis/experiments/L1_field/x158_g11_r30_s709.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r30_s709.compact.json) | other | 575149 | `085d2add859a5e7e21ecc314248cb1ca9e4ca25c65eda35b4dd1dc38d577bb13` |
| [`morphogenesis/experiments/L1_field/x158_g11_r45_s701.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r45_s701.compact.json) | other | 534187 | `34a8c2eaa7a78e701197aff7202de19f3f2084cca037ce69c01b0d7ff5328218` |
| [`morphogenesis/experiments/L1_field/x158_g11_r45_s702.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r45_s702.compact.json) | other | 573038 | `79bdde49221904d9ab54563042a169d03bec00433b3f5ccde1103de7440187f7` |
| [`morphogenesis/experiments/L1_field/x158_g11_r45_s703.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r45_s703.compact.json) | other | 559497 | `09057ef90beca057df48ddd5acf28be399d71d8966aca48ffe389836791e26e0` |
| [`morphogenesis/experiments/L1_field/x158_g11_r45_s704.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r45_s704.compact.json) | other | 544200 | `02150df123bb8c838751bac3b424789e666dabcf1525a5072577dd8b414ccb1d` |
| [`morphogenesis/experiments/L1_field/x158_g11_r45_s705.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r45_s705.compact.json) | other | 551048 | `f646971b0e22492fc166df6e90381ec59d0dd0e662f5888efab3d1a49ff9f351` |
| [`morphogenesis/experiments/L1_field/x158_g11_r45_s706.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r45_s706.compact.json) | other | 545611 | `14233f988dcd5036f8864703bd8867614c677233ee1ea721d6066961e56ab626` |
| [`morphogenesis/experiments/L1_field/x158_g11_r45_s707.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r45_s707.compact.json) | other | 554328 | `23c642f95efa2e2ce123592a01dcc0eb1a121aa0d074923d2070b9ad3e52687c` |
| [`morphogenesis/experiments/L1_field/x158_g11_r45_s708.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r45_s708.compact.json) | other | 545746 | `599aabf19440e64744c14e028c470270fd26c0b92cf758d7cfb8d5577d3e5943` |
| [`morphogenesis/experiments/L1_field/x158_g11_r45_s709.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r45_s709.compact.json) | other | 582129 | `5f54ab639856bcd712439340d47aac0296ea9875671e87581d6916cd708a4da4` |
| [`morphogenesis/experiments/L1_field/x158_g11_r60_s701.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r60_s701.compact.json) | other | 569353 | `e58ece89d49a54cb89f399b741672b5c16de723b2e1dd1d31e7d21cf2af093a0` |
| [`morphogenesis/experiments/L1_field/x158_g11_r60_s702.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r60_s702.compact.json) | other | 594013 | `151bdfdc2192259c836b1e42097481e193f3395abeadc387a8ef92ef2695b4b2` |
| [`morphogenesis/experiments/L1_field/x158_g11_r60_s703.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r60_s703.compact.json) | other | 588390 | `fed31f0134b16e47b96558e3d67aaf64963ae8e9df0faf72e1acce6ce3ed5e91` |
| [`morphogenesis/experiments/L1_field/x158_g11_r60_s704.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r60_s704.compact.json) | other | 585862 | `8f893149d13a12b2bf0db642a3054a814da7564236d6ea0e4f5bec13c32f34f1` |
| [`morphogenesis/experiments/L1_field/x158_g11_r60_s705.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r60_s705.compact.json) | other | 604286 | `31627a74b21adb9b453ca446f833c4be7b8c733f709453776231fb4b60934e32` |
| [`morphogenesis/experiments/L1_field/x158_g11_r60_s706.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r60_s706.compact.json) | other | 567036 | `50318359b15f4ebef040bca7b389039d9a27251e5aefe94e675aa9b51b54b40f` |
| [`morphogenesis/experiments/L1_field/x158_g11_r60_s707.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r60_s707.compact.json) | other | 606281 | `8c08547b67010a60ebceecfea5fc782aafc5232f8d9c938095bfc419b9d1d490` |
| [`morphogenesis/experiments/L1_field/x158_g11_r60_s708.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r60_s708.compact.json) | other | 566590 | `3285e621eb8556160f9a2459f76bc77a66b79e96f54a9031aa3928d2bed79cee` |
| [`morphogenesis/experiments/L1_field/x158_g11_r60_s709.compact.json`](../morphogenesis/experiments/L1_field/x158_g11_r60_s709.compact.json) | other | 559453 | `f68023899872acd1c72c4546563e1992187106eb18cbb172a01f41c1328297a2` |
| [`morphogenesis/experiments/L1_field/x158_g9_r60_s701.compact.json`](../morphogenesis/experiments/L1_field/x158_g9_r60_s701.compact.json) | other | 545845 | `216d3c27bb8380a67023050e95c303e63d828f52e6859160991fcd3ac7a92062` |
| [`morphogenesis/experiments/L1_field/x158_g9_r60_s702.compact.json`](../morphogenesis/experiments/L1_field/x158_g9_r60_s702.compact.json) | other | 576120 | `7404e092b03820ef5606f9e468cdd5a955659c5c667cc1c3e23e2a247c00fca2` |
| [`morphogenesis/experiments/L1_field/x158_g9_r60_s703.compact.json`](../morphogenesis/experiments/L1_field/x158_g9_r60_s703.compact.json) | other | 541025 | `16cf44d94806e665f449ca8d798f9ebcce97700d2f87fb2f6e06d6d188f58d31` |
| [`morphogenesis/experiments/L1_field/x158_g9_r60_s704.compact.json`](../morphogenesis/experiments/L1_field/x158_g9_r60_s704.compact.json) | other | 586805 | `7ec049272ec696ade5e97aa110f2f5fb7bd09a77651545a94b8ab9ad31e8157f` |
| [`morphogenesis/experiments/L1_field/x158_g9_r60_s705.compact.json`](../morphogenesis/experiments/L1_field/x158_g9_r60_s705.compact.json) | other | 531722 | `de49b1770a2d650eda482a99933b157859de7a3737f38d4e7872934c4d9fe12f` |
| [`morphogenesis/experiments/L1_field/x158_g9_r60_s706.compact.json`](../morphogenesis/experiments/L1_field/x158_g9_r60_s706.compact.json) | other | 534158 | `921c7039233116a9bea7a19b0b029f6cdb20f36139c8a957767a58cb54874b8f` |
| [`morphogenesis/experiments/L1_field/x158_g9_r60_s707.compact.json`](../morphogenesis/experiments/L1_field/x158_g9_r60_s707.compact.json) | other | 531487 | `f9457b1b56bc6ff0502e04c30b573196f9c436c76753e81a3960b33e326116ab` |
| [`morphogenesis/experiments/L1_field/x158_g9_r60_s708.compact.json`](../morphogenesis/experiments/L1_field/x158_g9_r60_s708.compact.json) | other | 533823 | `6f28326f50d22a7285d8af602fe377cb476587560c0216bce73d280bfd4993ec` |
| [`morphogenesis/experiments/L1_field/x158_g9_r60_s709.compact.json`](../morphogenesis/experiments/L1_field/x158_g9_r60_s709.compact.json) | other | 551547 | `7bb4bd5eb4f3cc875db140707360b302e18ec96945e71808f8ae493b941d40d1` |
| [`morphogenesis/experiments/L1_field/x158_series_index.json`](../morphogenesis/experiments/L1_field/x158_series_index.json) | other | 852 | `d2cf0f26691eee6de102fd67f5d843ea808077cbfd2e71299ac62ed65b84e8a0` |
| [`morphogenesis/experiments/L1_field/x158_series_index_r30.json`](../morphogenesis/experiments/L1_field/x158_series_index_r30.json) | other | 2118 | `ba7451e6b877d433ce8c7df89b7e3a8219f95858aa4eb87c1c74a15ddf6be5d1` |
| [`morphogenesis/experiments/L1_field/x158_series_index_r45.json`](../morphogenesis/experiments/L1_field/x158_series_index_r45.json) | other | 2119 | `088c6f0e290e156fc03e67baf682cf883b773d8ab2a371a9bd95ef89670fe1ee` |
| [`morphogenesis/experiments/L1_field/x158_series_index_r60.json`](../morphogenesis/experiments/L1_field/x158_series_index_r60.json) | other | 3142 | `0219aab5ae9f36d591aab35b292d22b95084d9e75d5f04056ed0c56f280a3e29` |
| [`morphogenesis/experiments/L1_field/x15_homog_s171.json`](../morphogenesis/experiments/L1_field/x15_homog_s171.json) | other | 4209 | `da2288eeb977dc2aad8d34f705ce3ecdae2c91746fbe62b16aaceb73283dbd47` |
| [`morphogenesis/experiments/L1_field/x15_homog_s172.json`](../morphogenesis/experiments/L1_field/x15_homog_s172.json) | other | 4229 | `4db7bc7c57bf720a350debd985365602c1a4857531aa8ba65797adf2f941e57f` |
| [`morphogenesis/experiments/L1_field/x15_homog_s173.json`](../morphogenesis/experiments/L1_field/x15_homog_s173.json) | other | 4131 | `f4aed52d23ba25fe2b9b9389cbcbf798e639a741920d846bf1a93ab01a49dd5e` |
| [`morphogenesis/experiments/L1_field/x15_homog_s174.json`](../morphogenesis/experiments/L1_field/x15_homog_s174.json) | other | 4320 | `ff541ca20e96a61c223ef2e4068b32af911ce28aff79cc85dc80847376f3b716` |
| [`morphogenesis/experiments/L1_field/x15_homog_s175.json`](../morphogenesis/experiments/L1_field/x15_homog_s175.json) | other | 4135 | `86f0c235a5f5c18917e00eeca01de61293bd57072e206ea2feca62436440f3b4` |
| [`morphogenesis/experiments/L1_field/x15_homog_s176.json`](../morphogenesis/experiments/L1_field/x15_homog_s176.json) | other | 4290 | `2934d9649cc60547a4998516c82f8efd12acd35d9827e8c2eaf22b99a2ecda09` |
| [`morphogenesis/experiments/L1_field/x15_homog_s177.json`](../morphogenesis/experiments/L1_field/x15_homog_s177.json) | other | 4159 | `536f31c367f52012859fbd4e587eaad605074efc6f9d624f985bb4e8a9b94b91` |
| [`morphogenesis/experiments/L1_field/x15_homog_s178.json`](../morphogenesis/experiments/L1_field/x15_homog_s178.json) | other | 4407 | `8eb066a9902912c4c3ed2b847ebd95fef1e477f5c046aca9f1129f88a1653c3f` |
| [`morphogenesis/experiments/L1_field/x15_homog_s179.json`](../morphogenesis/experiments/L1_field/x15_homog_s179.json) | other | 4208 | `fe04a86278fd440a8048ef9294e84752b60611ce6aa0c35943292a30fa9a8fff` |
| [`morphogenesis/experiments/L1_field/x15_homog_s180.json`](../morphogenesis/experiments/L1_field/x15_homog_s180.json) | other | 4155 | `51dd55a18dcacfb1378a021f762206ef7cb915d218bd527b2929d500ba6d5d3f` |
| [`morphogenesis/experiments/L1_field/x15_homog_s181.json`](../morphogenesis/experiments/L1_field/x15_homog_s181.json) | other | 4419 | `1be34add17316af337ec5481885e3100c8869953f5c45e5ba23aabadfaf833b6` |
| [`morphogenesis/experiments/L1_field/x15_homog_s182.json`](../morphogenesis/experiments/L1_field/x15_homog_s182.json) | other | 4225 | `558fbd620bf403921e4a19ee1307bcec185c99de480c9143bdacc37256c581a8` |
| [`morphogenesis/experiments/L1_field/x15_homog_s183.json`](../morphogenesis/experiments/L1_field/x15_homog_s183.json) | other | 4108 | `7fc4934b8b82de5a5685d8fdb152d18737e763c79724a1b0468462e576134fed` |
| [`morphogenesis/experiments/L1_field/x15_homog_s184.json`](../morphogenesis/experiments/L1_field/x15_homog_s184.json) | other | 4226 | `77f9f789cd496a76dcae650e6ad998d7b2d9108f98cae542342424ff9aee798b` |
| [`morphogenesis/experiments/L1_field/x15_homog_s185.json`](../morphogenesis/experiments/L1_field/x15_homog_s185.json) | other | 4264 | `606c51b87988876d5c03cdc4d2fe238ea57ded9dd9cba2d415f6fd52fb794724` |
| [`morphogenesis/experiments/L1_field/x15_homog_s186.json`](../morphogenesis/experiments/L1_field/x15_homog_s186.json) | other | 4613 | `4d3cf13fcf074affdb4a72445630a2130b5f0a4baaccf8ff6164ac859aba1b43` |
| [`morphogenesis/experiments/L1_field/x15_homog_s187.json`](../morphogenesis/experiments/L1_field/x15_homog_s187.json) | other | 4325 | `f3bc978e8ea63aed30b4f39f152b779e488e735e834afc95daa0a32bef9a7542` |
| [`morphogenesis/experiments/L1_field/x15_homog_s188.json`](../morphogenesis/experiments/L1_field/x15_homog_s188.json) | other | 4205 | `23a135c2468fc00512cf78083d5127fe50ac97be7dcfca078da027ed35f8d100` |
| [`morphogenesis/experiments/L1_field/x15_homog_s189.json`](../morphogenesis/experiments/L1_field/x15_homog_s189.json) | other | 4151 | `0ccc589a7163fb82e1a7fe478febb1d03ffadc04e5da4ab72fb93840a327ddcb` |
| [`morphogenesis/experiments/L1_field/x15_homog_s190.json`](../morphogenesis/experiments/L1_field/x15_homog_s190.json) | other | 4482 | `d37bda38291d609dec57cf800662908f69f1fb25b77c49b92032831f9c292c11` |
| [`morphogenesis/experiments/L1_field/x164_asym_g10_s931.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g10_s931.compact.json) | other | 617939 | `2da17b6c137ce431a12a32f0ceeae6a68b6ba7a1cdc4d17cc1da4897fc5e9b3b` |
| [`morphogenesis/experiments/L1_field/x164_asym_g10_s932.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g10_s932.compact.json) | other | 575034 | `f8fc9d0e748e9cb6ebdb4d5434fafc0efc54440c52d40590769d2812cc54597e` |
| [`morphogenesis/experiments/L1_field/x164_asym_g10_s933.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g10_s933.compact.json) | other | 565640 | `e1bbf3f0f05e4ceb218cd6a4affcfdd7d14d09866f28f21821c64d0e007ac640` |
| [`morphogenesis/experiments/L1_field/x164_asym_g10_s934.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g10_s934.compact.json) | other | 578160 | `1f94a031096b38fef0b077768eded6d35432427a1103966b2665abe90339d0fd` |
| [`morphogenesis/experiments/L1_field/x164_asym_g10_s935.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g10_s935.compact.json) | other | 539814 | `228fd3230089e45ceb43a7890cf4022e956d9790962489f35e7568d1b9ebaf62` |
| [`morphogenesis/experiments/L1_field/x164_asym_g4_s931.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g4_s931.compact.json) | other | 602047 | `a265dd96daaaad37205588e2d5084c3c8f52c9f10421dfede1c1524ea427fe86` |
| [`morphogenesis/experiments/L1_field/x164_asym_g4_s932.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g4_s932.compact.json) | other | 551349 | `d47ac5d3ec61e5805193350b6ae99001d4332e8e78d6df7a4d1333b32500c0b1` |
| [`morphogenesis/experiments/L1_field/x164_asym_g4_s933.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g4_s933.compact.json) | other | 574141 | `a74e0dfe4994c7d1d5bc8de455f2a03435fc04b6390186ffbe5ae4d00d2e54be` |
| [`morphogenesis/experiments/L1_field/x164_asym_g4_s934.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g4_s934.compact.json) | other | 574783 | `563184c46fe530db43fd4dd813e14f7b223c00fce773e1025e4f94250cc2ec7b` |
| [`morphogenesis/experiments/L1_field/x164_asym_g4_s935.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g4_s935.compact.json) | other | 588036 | `9eb3394e53719329c6598395c55b7d0e55c6f8d5f0d312cff944a5b686b02c7d` |
| [`morphogenesis/experiments/L1_field/x164_asym_g6_s931.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g6_s931.compact.json) | other | 584405 | `b2d15f022036fa57ddd37dd893c68c3713166d3b5f9f35d45493e1d5eef39a00` |
| [`morphogenesis/experiments/L1_field/x164_asym_g6_s932.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g6_s932.compact.json) | other | 493765 | `a98424e9c1f551eac149f43bf8904799e28af55348b348ff88e9f13be64a4dff` |
| [`morphogenesis/experiments/L1_field/x164_asym_g6_s933.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g6_s933.compact.json) | other | 569070 | `bf12c95ad5d93577dbf7c7b816a5ba3a46ce177c25e7a879b93a48faf5dacbf9` |
| [`morphogenesis/experiments/L1_field/x164_asym_g6_s934.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g6_s934.compact.json) | other | 589712 | `2ac0a735d1a406dd8a77b80e5a15585d135f4e5597361a95db10e2069f5ec134` |
| [`morphogenesis/experiments/L1_field/x164_asym_g6_s935.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g6_s935.compact.json) | other | 569593 | `512f3a465977f892ddf31d9ca713d16df08aba178ab113010d168e0d62a4e02e` |
| [`morphogenesis/experiments/L1_field/x164_asym_g8_s931.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g8_s931.compact.json) | other | 577868 | `62abebc95ece9b6e378bab2bd7a94e3dd5046219bc39b6bd36d8b7a208b15617` |
| [`morphogenesis/experiments/L1_field/x164_asym_g8_s932.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g8_s932.compact.json) | other | 609376 | `9e2475cf4d3a188cb6e531b2c0347454a17e85b0237d54b28d49a219e4ac140a` |
| [`morphogenesis/experiments/L1_field/x164_asym_g8_s933.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g8_s933.compact.json) | other | 582539 | `58eedb1baf33bb48677cea3424a7a537316dc5b2c94d36573d56af3b267c38bd` |
| [`morphogenesis/experiments/L1_field/x164_asym_g8_s934.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g8_s934.compact.json) | other | 604155 | `d48b9a38a365a2028e571810a06db4e47dc8ef41a9307a73a60e42cac7c3bfe5` |
| [`morphogenesis/experiments/L1_field/x164_asym_g8_s935.compact.json`](../morphogenesis/experiments/L1_field/x164_asym_g8_s935.compact.json) | other | 556798 | `0aa75a79a6996b2b1e845bf9a5503cf2fb504186385c2675e03b1a492136c0b1` |
| [`morphogenesis/experiments/L1_field/x164_series_index.json`](../morphogenesis/experiments/L1_field/x164_series_index.json) | other | 3238 | `1db71f1934b8baab9ffc32373c0db6dff5cccb28a9870d9b01f71c4539cbbe69` |
| [`morphogenesis/experiments/L1_field/x164_sym_r3_g8_s931.compact.json`](../morphogenesis/experiments/L1_field/x164_sym_r3_g8_s931.compact.json) | other | 553933 | `a971cf4da9191fdf57232d173eedff536f3ac1eb95f6b0bff21a334fe68326b2` |
| [`morphogenesis/experiments/L1_field/x164_sym_r3_g8_s932.compact.json`](../morphogenesis/experiments/L1_field/x164_sym_r3_g8_s932.compact.json) | other | 547124 | `8156a847d656f1c4b59e60e34fcac4e4dd0268a14c61094108cce7aeaf865011` |
| [`morphogenesis/experiments/L1_field/x164_sym_r3_g8_s933.compact.json`](../morphogenesis/experiments/L1_field/x164_sym_r3_g8_s933.compact.json) | other | 547367 | `535e0587b25c911121c6de3562555023e1240cdfbab49671af4a501aa830d765` |
| [`morphogenesis/experiments/L1_field/x164_sym_r3_g8_s934.compact.json`](../morphogenesis/experiments/L1_field/x164_sym_r3_g8_s934.compact.json) | other | 573052 | `49ccc76d6cb0015fda602d15160b7032d31425a8ab15f905ec8a22b6ec2bfaa9` |
| [`morphogenesis/experiments/L1_field/x164_sym_r3_g8_s935.compact.json`](../morphogenesis/experiments/L1_field/x164_sym_r3_g8_s935.compact.json) | other | 548223 | `07126e7ca91e278508985a7e86d636a09bcc378a9dbcc857ca8177e1fce90c92` |
| [`morphogenesis/experiments/L1_field/x164_sym_r6_g8_s931.compact.json`](../morphogenesis/experiments/L1_field/x164_sym_r6_g8_s931.compact.json) | other | 546577 | `86c6fabee663f5241373e7b649e0bcd84f7e2ab8cb3be8b7e2f3ce7e6aa24cc8` |
| [`morphogenesis/experiments/L1_field/x164_sym_r6_g8_s932.compact.json`](../morphogenesis/experiments/L1_field/x164_sym_r6_g8_s932.compact.json) | other | 586792 | `3fa85c3284e55aa303d7013f55b3c9164a595155b47e8cb587e34c76569c1031` |
| [`morphogenesis/experiments/L1_field/x164_sym_r6_g8_s933.compact.json`](../morphogenesis/experiments/L1_field/x164_sym_r6_g8_s933.compact.json) | other | 586153 | `f4f2a90ee01c955c8e919410d3acb398acc16bd8654b31103567b3f33bbeb20f` |
| [`morphogenesis/experiments/L1_field/x164_sym_r6_g8_s934.compact.json`](../morphogenesis/experiments/L1_field/x164_sym_r6_g8_s934.compact.json) | other | 616180 | `12b8c3d25dc0e7b1475f8dcca9502d9738a9747e623b0f4febae545d6c15ad53` |
| [`morphogenesis/experiments/L1_field/x164_sym_r6_g8_s935.compact.json`](../morphogenesis/experiments/L1_field/x164_sym_r6_g8_s935.compact.json) | other | 556369 | `181ec54424ad657998dbe9b1123903d3474f1b84d2c6c16dfce1de442ffbd546` |
| [`morphogenesis/experiments/L1_field/x165_row3_g10_s981.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g10_s981.compact.json) | other | 613202 | `4eb1d67bab401e90bb6bb610c8acb2acbbe87bb389cdfdb9d783115d68b76aff` |
| [`morphogenesis/experiments/L1_field/x165_row3_g10_s982.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g10_s982.compact.json) | other | 626591 | `760c955ee4e5d024f516cb8d047b6c5f23d7333423effb8a04f34b0efe90d681` |
| [`morphogenesis/experiments/L1_field/x165_row3_g10_s983.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g10_s983.compact.json) | other | 626437 | `919d95076eecb27b5240696ed9e2ff8b1ee85468300ac6eb40308c5eee767982` |
| [`morphogenesis/experiments/L1_field/x165_row3_g10_s984.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g10_s984.compact.json) | other | 618265 | `5c8dbcf08e0fe331cf5af9e7d552377dde95df3fa76790e55af74268e353ac83` |
| [`morphogenesis/experiments/L1_field/x165_row3_g10_s985.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g10_s985.compact.json) | other | 626437 | `660d678b69582518cfbad639295fd1c55b41a67bf96d009fa699901fd645a319` |
| [`morphogenesis/experiments/L1_field/x165_row3_g12_s981.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g12_s981.compact.json) | other | 609025 | `5a58a4e5ceb474d0e2d3add765eeca223b20dc8db7fcbb6b6cae9fdf73ceceaa` |
| [`morphogenesis/experiments/L1_field/x165_row3_g12_s982.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g12_s982.compact.json) | other | 647481 | `29df911269e81ed2b860cca1142a975c7b90549390491f9ad2b9657688456e5d` |
| [`morphogenesis/experiments/L1_field/x165_row3_g12_s983.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g12_s983.compact.json) | other | 647558 | `287cd53e258fc75f8b0708ce699cd6016fb9c93a33d1ec2427692706f7fc1e9a` |
| [`morphogenesis/experiments/L1_field/x165_row3_g12_s984.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g12_s984.compact.json) | other | 685753 | `8c739334b8c4914bb209c07d10f219e0fb52fda964ddaf8ce4614135e069875f` |
| [`morphogenesis/experiments/L1_field/x165_row3_g12_s985.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g12_s985.compact.json) | other | 647558 | `48f5313761f9b6f74a4efd60ec47a3c2694ecfa64ef865291aacf92893fc78a0` |
| [`morphogenesis/experiments/L1_field/x165_row3_g8_s981.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g8_s981.compact.json) | other | 594976 | `50ec077e00904a1a779e00967f267a6101e0b45cc3d3c1572778ad2b5c37f40b` |
| [`morphogenesis/experiments/L1_field/x165_row3_g8_s982.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g8_s982.compact.json) | other | 571695 | `5c43b2ff4e3fac2d59167d232ea16099b4555a885797ffa1a0176bcab892d0d8` |
| [`morphogenesis/experiments/L1_field/x165_row3_g8_s983.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g8_s983.compact.json) | other | 573132 | `4a96fba5f2a1a28efcaf3daca0b8806fb628c8e42bf0b5d1cf1b52bf3b60fd35` |
| [`morphogenesis/experiments/L1_field/x165_row3_g8_s984.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g8_s984.compact.json) | other | 563633 | `af563fb06fdc0d3062ba16d354b22702971b1d6c763c8aac0d6c0c5a99f57aff` |
| [`morphogenesis/experiments/L1_field/x165_row3_g8_s985.compact.json`](../morphogenesis/experiments/L1_field/x165_row3_g8_s985.compact.json) | other | 573132 | `bf8523829e18088b4e7c823a7ce99ae3c153f1afc2ad9bc51282edcd9500cb6d` |
| [`morphogenesis/experiments/L1_field/x165_series_index.json`](../morphogenesis/experiments/L1_field/x165_series_index.json) | other | 1346 | `12a2e7b3cebdb86b8145f638a7095b0a001a69739bc7820b8d53a6c9656cc501` |
| [`morphogenesis/experiments/L1_field/x166_series_index.json`](../morphogenesis/experiments/L1_field/x166_series_index.json) | other | 2768 | `bc3e35c28557c56855888271be4bd63a45866af98850ddca062f72cd8c82f384` |
| [`morphogenesis/experiments/L1_field/x167b_series_index.json`](../morphogenesis/experiments/L1_field/x167b_series_index.json) | other | 791 | `f91c8a56c015152df38e7841706cb26bbe2f3150641da4ee9137fb62d4f68cc6` |
| [`morphogenesis/experiments/L1_field/x167b_single_s951.compact.json`](../morphogenesis/experiments/L1_field/x167b_single_s951.compact.json) | other | 132102 | `237b2a4ad584906e5445f091c4e06e0760a9b95c948a18d1d3fdb07c81afd2ba` |
| [`morphogenesis/experiments/L1_field/x167b_single_s952.compact.json`](../morphogenesis/experiments/L1_field/x167b_single_s952.compact.json) | other | 162410 | `12ca0669a7d5a5de20ed450bea7870efc98ebd78d4159e481a2bf0005ab96d3c` |
| [`morphogenesis/experiments/L1_field/x167b_single_s953.compact.json`](../morphogenesis/experiments/L1_field/x167b_single_s953.compact.json) | other | 163156 | `85443b208d8c889de3f4ff760047eb27c3efd2ca02e827ade7b339fb1f5061be` |
| [`morphogenesis/experiments/L1_field/x167b_single_s954.compact.json`](../morphogenesis/experiments/L1_field/x167b_single_s954.compact.json) | other | 175784 | `9de735115f82339a7e57b7b99e6097816c306211c9c652a388e71fe0fc7b92c5` |
| [`morphogenesis/experiments/L1_field/x167b_single_s955.compact.json`](../morphogenesis/experiments/L1_field/x167b_single_s955.compact.json) | other | 162540 | `3e345f5096267d305d59f65df50c2b4acfda4025494482ef922cd59a5e78d3b7` |
| [`morphogenesis/experiments/L1_field/x167b_single_s956.compact.json`](../morphogenesis/experiments/L1_field/x167b_single_s956.compact.json) | other | 170006 | `c4617b5975cc5068a0db000525703d5a8e92d9b5549333434ba9dc78c2ec97b8` |
| [`morphogenesis/experiments/L1_field/x167b_single_s957.compact.json`](../morphogenesis/experiments/L1_field/x167b_single_s957.compact.json) | other | 172712 | `5d8f8c45e676286497ffbd34d1a37932f4aac8445c97abedd850da3599933485` |
| [`morphogenesis/experiments/L1_field/x167b_single_s958.compact.json`](../morphogenesis/experiments/L1_field/x167b_single_s958.compact.json) | other | 163942 | `f6e8f11401290d2aa7a43552d39b01fce483488cb5d4fd279d36869eed5fafcc` |
| [`morphogenesis/experiments/L1_field/x167b_single_s959.compact.json`](../morphogenesis/experiments/L1_field/x167b_single_s959.compact.json) | other | 188990 | `f4570075a9ae83d60c976dcf4a97a72e938e09fab0aede642685ca97834d28d4` |
| [`morphogenesis/experiments/L1_field/x167b_single_s960.compact.json`](../morphogenesis/experiments/L1_field/x167b_single_s960.compact.json) | other | 161171 | `e133cd27cb3f9cbde4897414ea5e30bd4ef8604378fff9f95228b67cae44abd2` |
| [`morphogenesis/experiments/L1_field/x168_F26_g11_s961.compact.json`](../morphogenesis/experiments/L1_field/x168_F26_g11_s961.compact.json) | other | 60203 | `1a78e4ca72ed1968fc6cd1d41581e3eae3dcf59a97654cf7148365839af85a33` |
| [`morphogenesis/experiments/L1_field/x168_F26_g11_s962.compact.json`](../morphogenesis/experiments/L1_field/x168_F26_g11_s962.compact.json) | other | 57780 | `913afbeb89f1030efce87010cad2bd6ae09557258ca086d7aa512d3830ffbb9c` |
| [`morphogenesis/experiments/L1_field/x168_F26_g11_s963.compact.json`](../morphogenesis/experiments/L1_field/x168_F26_g11_s963.compact.json) | other | 58269 | `71bdc515e53cd4ec18dd9dee7fd6ae86ddf2fd39c57678f6736e806ca93cdc9e` |
| [`morphogenesis/experiments/L1_field/x168_F26_g11_s964.compact.json`](../morphogenesis/experiments/L1_field/x168_F26_g11_s964.compact.json) | other | 59351 | `cc781c1d98bfee11af0a41a1d14358abad90edfc4e98d4236e3863bff59a9cb0` |
| [`morphogenesis/experiments/L1_field/x168_F26_g11_s965.compact.json`](../morphogenesis/experiments/L1_field/x168_F26_g11_s965.compact.json) | other | 58912 | `a5f8c1e5ad31d71185fe83d2af46bd29c8dc03904913c48f239b21c3f12d46ec` |
| [`morphogenesis/experiments/L1_field/x168_F26_g8_s961.compact.json`](../morphogenesis/experiments/L1_field/x168_F26_g8_s961.compact.json) | other | 56026 | `d553f32f6a7b9c1ba9f5699ba0c1b178634e50b810264bf1257c65d98aa40a1e` |
| [`morphogenesis/experiments/L1_field/x168_F26_g8_s962.compact.json`](../morphogenesis/experiments/L1_field/x168_F26_g8_s962.compact.json) | other | 55362 | `d137eda125b3e465c61adf26c5bb611e0c7a6b6c2e3b6615a10a751b9294186f` |
| [`morphogenesis/experiments/L1_field/x168_F26_g8_s963.compact.json`](../morphogenesis/experiments/L1_field/x168_F26_g8_s963.compact.json) | other | 56723 | `365ce8ac85812de511e2219d22ae7dfb7dcfaf27ed70d5e6d95ef20272166753` |
| [`morphogenesis/experiments/L1_field/x168_F26_g8_s964.compact.json`](../morphogenesis/experiments/L1_field/x168_F26_g8_s964.compact.json) | other | 61191 | `25940093abcd4fdd9052d96c2fb15a30fc39148af74ebbf9d18ee2b9774c74b5` |
| [`morphogenesis/experiments/L1_field/x168_F26_g8_s965.compact.json`](../morphogenesis/experiments/L1_field/x168_F26_g8_s965.compact.json) | other | 56308 | `f20b94d517ba1e5d749775c930853895afe933d92291192d3fe606f41c69b510` |
| [`morphogenesis/experiments/L1_field/x168_F36_g11_s961.compact.json`](../morphogenesis/experiments/L1_field/x168_F36_g11_s961.compact.json) | other | 67992 | `58196e2c3ad9f913683d0342c090c6a27972c76c35d4ef6ddc7b02b437b2a381` |
| [`morphogenesis/experiments/L1_field/x168_F36_g11_s962.compact.json`](../morphogenesis/experiments/L1_field/x168_F36_g11_s962.compact.json) | other | 58123 | `db78bfd07a44bc92d3d65c9dfe4fdbb4f07027413d13a3a305033b795a8bb8f2` |
| [`morphogenesis/experiments/L1_field/x168_F36_g11_s963.compact.json`](../morphogenesis/experiments/L1_field/x168_F36_g11_s963.compact.json) | other | 69991 | `77bbd15026fc1145412a42a0c4c522fcfb13156645d053b37acdd6a9d0db3394` |
| [`morphogenesis/experiments/L1_field/x168_F36_g11_s964.compact.json`](../morphogenesis/experiments/L1_field/x168_F36_g11_s964.compact.json) | other | 63285 | `abaa02f78b96dfb8f9817ed7bf87324d7b8ea1ce503bab1d3cd565fbae0b2510` |
| [`morphogenesis/experiments/L1_field/x168_F36_g11_s965.compact.json`](../morphogenesis/experiments/L1_field/x168_F36_g11_s965.compact.json) | other | 61418 | `49c53606871e8385d4e0fc630877476eb2d2db80202c7a6ca46c5088cdad519f` |
| [`morphogenesis/experiments/L1_field/x168_F36_g8_s961.compact.json`](../morphogenesis/experiments/L1_field/x168_F36_g8_s961.compact.json) | other | 62543 | `0516807412fbfb51f6dae1ecf039ce9afa18a089534539c52fd598392bf4c392` |
| [`morphogenesis/experiments/L1_field/x168_F36_g8_s962.compact.json`](../morphogenesis/experiments/L1_field/x168_F36_g8_s962.compact.json) | other | 61032 | `f1b283034b93c749fd72811f61916ce0c0ac24e24f15e5fe761879821e13ccd7` |
| [`morphogenesis/experiments/L1_field/x168_F36_g8_s963.compact.json`](../morphogenesis/experiments/L1_field/x168_F36_g8_s963.compact.json) | other | 69922 | `30a2bb8f782857a4e75488ce3b996b0c53fd547cffe1ab52157128775f2c605e` |
| [`morphogenesis/experiments/L1_field/x168_F36_g8_s964.compact.json`](../morphogenesis/experiments/L1_field/x168_F36_g8_s964.compact.json) | other | 64219 | `b812bc92bcd96feabe3f8e16e0d7be36139823f086e956b1bee64d8d9487d6f7` |
| [`morphogenesis/experiments/L1_field/x168_F36_g8_s965.compact.json`](../morphogenesis/experiments/L1_field/x168_F36_g8_s965.compact.json) | other | 62530 | `8b0d31ba25a92d4964f26c3892701f67ebdfe1d8112525f637390b94ce8694f2` |
| [`morphogenesis/experiments/L1_field/x168_series_index.json`](../morphogenesis/experiments/L1_field/x168_series_index.json) | other | 2099 | `28c6a8f9f05532f6528ae85cf470571bbda1ac3653104260c282964a6f224b1d` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g12_s961.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g12_s961.compact.json) | other | 61284 | `53ff955955a398ce66cf8b11831a56087aee40d807b640c526baf962acee6748` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g12_s962.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g12_s962.compact.json) | other | 59407 | `3b20f579eec64ab18b7cfca9ad8a78efd1c6aebb3449164cda119c4010b6d592` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g12_s963.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g12_s963.compact.json) | other | 62817 | `df9b39b701f9eb5d2ff122dc8327a7e64961b32734ca65fa134111e520a74b66` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g12_s964.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g12_s964.compact.json) | other | 58384 | `4bf3c3cbd68b8ff3b8c44b5b9c735edcc55bcfb76f6e98dafcdff89260469512` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g12_s965.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g12_s965.compact.json) | other | 57712 | `d51730dacd453621f6b3a92ae5c0f32ca6af4999f19ee01fadb76119665b5ac1` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g14_s961.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g14_s961.compact.json) | other | 65638 | `51910e6f14aa562a71ff092c21ec7c67fad7cb2a48659225664962b9998c8b84` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g14_s962.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g14_s962.compact.json) | other | 61971 | `0fd792745041be9c670c835672e7d21affaee0ec835c1b13786c157c68f9a1ff` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g14_s963.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g14_s963.compact.json) | other | 62671 | `3274e47d47582eac13beb312d052b5d7a5a9499f1c963d27cb7059e2e18385fb` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g14_s964.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g14_s964.compact.json) | other | 62269 | `b83ba5c2c3769f8c4ef1060e568b3abc557b83e505558c96c834b5894dae3ae0` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g14_s965.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g14_s965.compact.json) | other | 60607 | `82b6313a7e6ba9d5ff5ae31ffb4ee24494b3d6d841d8574ef5eb2845d5cfb8aa` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g8_s961.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g8_s961.compact.json) | other | 56027 | `8aac1b9b3c7b26e229f42dac0ba09e80ceb107ceb2e3e69d52e809ac917a343a` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g8_s962.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g8_s962.compact.json) | other | 55363 | `ce8e77796dcddeea370ead4ef233d5af50969a7926caf0268e3fa02951274ce2` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g8_s963.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g8_s963.compact.json) | other | 56724 | `3f56085ee0f1c27867b5394b1587bef8507a90888d9b1e576190668518d07519` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g8_s964.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g8_s964.compact.json) | other | 61192 | `16d0b7c8ab75312c97d8a9664563818aea5454ad573ccd9357ab2117293e96ae` |
| [`morphogenesis/experiments/L1_field/x168b_F26_g8_s965.compact.json`](../morphogenesis/experiments/L1_field/x168b_F26_g8_s965.compact.json) | other | 56309 | `3cbb5642b0dc91372b87b3ad8d6af64988aace18711f8b9a446f3f1584711e4d` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g10_s961.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g10_s961.compact.json) | other | 65782 | `78fdd6a3e9ba1e7d87ca020d3fa6aeb1ce53538cb088d7fea9764cfcec57591f` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g10_s962.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g10_s962.compact.json) | other | 78509 | `d758fb1c632cfe1cac6d8110f96cbfc3e38973ceb543af7bd120f6ecd07a493d` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g10_s963.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g10_s963.compact.json) | other | 79618 | `9f2c059622ced084512f1bc40280ceb803b0b84c217057f69b4ad94962d1a877` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g10_s964.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g10_s964.compact.json) | other | 70343 | `d35762f3a0447e21acdada2c8a4506dc64f5defcd459b777560a1315a8afdffe` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g10_s965.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g10_s965.compact.json) | other | 70900 | `ffe943d52d16e9ed7b8670bf208d5094d294fcc0729fc69d374231500787cd30` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g11_s961.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g11_s961.compact.json) | other | 70693 | `fb799f726aa829d2473b00af1bfc195f38b658bfc76e821d91e64470308ed0fa` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g11_s962.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g11_s962.compact.json) | other | 78059 | `44aad016b266ac5f0b9b5a7a5ff1549a14a50329b23b88b8ff8c99792b9538fc` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g11_s963.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g11_s963.compact.json) | other | 78012 | `c3a8daef525ad3ed6dc24ad0f346143698f0306538189e976d23a49b7b15e694` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g11_s964.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g11_s964.compact.json) | other | 72378 | `22de772b12c300b96db8330f9a92bdb99f1ed8eb32bd29e8d9fae643bcd69295` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g11_s965.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g11_s965.compact.json) | other | 70497 | `1fcc63904a6ab70239b395c41ca8441254f56d40631939d7cbfd7734537fadd4` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g12_s961.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g12_s961.compact.json) | other | 76974 | `6f9f1224ad76b089888601ab83d08edfce581687f8316d1cc07a1fbab28f7b1b` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g12_s962.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g12_s962.compact.json) | other | 78530 | `3023b0713bcb62f8908a6d28dee310ff7341c8cca784c2af9243b5e67bf5a2c6` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g12_s963.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g12_s963.compact.json) | other | 75057 | `17579352511152b2ed2238ad18d2323d51510d8f5ac46932e47ba4ca428aa756` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g12_s964.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g12_s964.compact.json) | other | 72874 | `2551f8160de1f5f738905880a498924b4e75d51f751c8fa7b605b1b4737b7c46` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g12_s965.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g12_s965.compact.json) | other | 80006 | `41459f9f985f0bf2597d5772c419ee926eb7984b540103bbb8e3f339433ecc14` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g8_s961.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g8_s961.compact.json) | other | 78136 | `ce3e7d56fb7348919c5993ab92671d3ac943f40f45a99250523ae40a2a48449b` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g8_s962.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g8_s962.compact.json) | other | 73000 | `609952a16ef92b28bef65d7b7fc666688086ba43e2c385c38285f1c30a27764c` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g8_s963.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g8_s963.compact.json) | other | 77814 | `2d6850a501009fab8dee2b4bfeb874746d2b598a7687f57ee245956a22ecce4c` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g8_s964.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g8_s964.compact.json) | other | 68952 | `582ffedb853d1ebe0123b474b216711ecb969c7a99f1f0fc8a9935d0b71ff759` |
| [`morphogenesis/experiments/L1_field/x168b_F30_g8_s965.compact.json`](../morphogenesis/experiments/L1_field/x168b_F30_g8_s965.compact.json) | other | 71921 | `8c3142ffaa81a70f1009698a78fa50c39e79af4292db008e47057bade09a3967` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g12_s961.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g12_s961.compact.json) | other | 70750 | `8759c8497992db90826bf53aa14dd2116db71108c3c9d781d90bf5a25b202083` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g12_s962.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g12_s962.compact.json) | other | 60784 | `5a4e565d1c3ae0681d0558b53ee14834dcb563ce66d510ddf6d76d3e80a4bef7` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g12_s963.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g12_s963.compact.json) | other | 72375 | `7de20eb41fdf0c94eba9fa01d2f79af1bb77dac9b2c67426b1a531ad8f570ed6` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g12_s964.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g12_s964.compact.json) | other | 56601 | `5eb676ba630a90d23a1f18f3b903137f012a1a6c3041092585ec0b1935639ad4` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g12_s965.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g12_s965.compact.json) | other | 60097 | `f21ed7f75ec3894c113584d4592b954d304c9a0d860b864d2d8abe212560399b` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g14_s961.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g14_s961.compact.json) | other | 65666 | `11296f39885d3cece0277c2006f03052f2178cedf7445dd3253ca5876805d814` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g14_s962.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g14_s962.compact.json) | other | 68312 | `59a4ae598e32a6cf6ac8da5dcb1045f8d14a73b00392b85a8b76a4de58da869a` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g14_s963.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g14_s963.compact.json) | other | 76571 | `1119ab86a9f874c6c6e0af4295d452d24c7c9600b2260c2b8a9079f8fb1958d7` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g14_s964.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g14_s964.compact.json) | other | 64117 | `b9f57eb3e925414ef2920a05682ec4790764be9739555d8d24044e17a19edb12` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g14_s965.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g14_s965.compact.json) | other | 68826 | `f0aa91a3e9e314b5303e9148d92a62394b720c67d1443cf5de12069fbce72599` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g8_s961.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g8_s961.compact.json) | other | 62544 | `bfab584d0607c45b522e9bcb0fdff69e952f5eb3604b5d800ae90f974b1ed5a5` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g8_s962.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g8_s962.compact.json) | other | 61033 | `f22d3edb986c04c58028343aeafd7d0d784eed17b6bc1fe2d42d658d632aff24` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g8_s963.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g8_s963.compact.json) | other | 69923 | `dc80e9e4527bf9a38e14ddc9eafd46ad9022922e109315e6c5fa06346f53b231` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g8_s964.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g8_s964.compact.json) | other | 64220 | `35ead7e06d3bc9166409a227f36f896d31f575b81e4f3122db13cc30ef44f797` |
| [`morphogenesis/experiments/L1_field/x168b_F36_g8_s965.compact.json`](../morphogenesis/experiments/L1_field/x168b_F36_g8_s965.compact.json) | other | 62531 | `e29bbb6b8174a44ecf5c7f650f90b1f9d8c82d4b37f43f7b6bdd46a1f45f3434` |
| [`morphogenesis/experiments/L1_field/x168b_series_index.json`](../morphogenesis/experiments/L1_field/x168b_series_index.json) | other | 5077 | `a1b2f2372f55636242ac46a3d8b968528bb2d3b0151abacbb9f18e0c17eb2488` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g10_s961.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g10_s961.compact.json) | other | 63336 | `3ffbdefc93d3cdf0687b25ea7dda837ff4dfde05e526547b2b2a29be337d6e47` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g10_s962.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g10_s962.compact.json) | other | 54631 | `7a81240faeccf37eacfdd8d174e3ac7229a5720e45f0c99634525b2c303523ce` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g10_s963.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g10_s963.compact.json) | other | 62775 | `de5ad8eaa7807188e0f906e8d8eb06b4c4c25d5f16e876dca7e6ce7d4d3d0200` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g10_s964.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g10_s964.compact.json) | other | 67747 | `a1603c7548f749b4511b8569d86579d13994105c250a9c94bc22f1717d6bd1a7` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g10_s965.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g10_s965.compact.json) | other | 64795 | `bd8cee13c7e4133bf475a23d0d988252922c304be06341137fe7ee1579cbf883` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g11_s961.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g11_s961.compact.json) | other | 63396 | `ca3dfccd325b9fbfd8c59bbbc59c5a626d4a019d3f739494fef3b7510821d630` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g11_s962.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g11_s962.compact.json) | other | 60295 | `e12de94dc875516e920cb72790914f97a654679c1f11f8427975f2df19e2281d` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g11_s963.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g11_s963.compact.json) | other | 63561 | `9601e518f6f22e40622ed75947bab140d92ab865aee5ff00997276b9d4047835` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g11_s964.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g11_s964.compact.json) | other | 65345 | `5d72e182ea205f531696be7584f9e2d7455b9144058b8e578b4bf2cfad5af02c` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g11_s965.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g11_s965.compact.json) | other | 64408 | `ca944aab15a313d3eff451ecf9c710fa88d427006034acaef29ab20f241bdd1c` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g8_s961.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g8_s961.compact.json) | other | 65637 | `bab9252867d749c8ed45ef7785384960ccda291d67fd8d39b5073a3d85dc8244` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g8_s962.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g8_s962.compact.json) | other | 61970 | `6420e5c287231329248206f382aeeee716051176e25c37800cd946c9915c7a8f` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g8_s963.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g8_s963.compact.json) | other | 62670 | `761a27ced3f2c87007d0e9b46cc6f0b53049dc97afc6bed2c96b7ec004029f1b` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g8_s964.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g8_s964.compact.json) | other | 62268 | `421b05a5452bd92e7765a2cc32913c8bc362dc0ed9d7d0aef0be03e1168960ce` |
| [`morphogenesis/experiments/L1_field/x168c_F26_g8_s965.compact.json`](../morphogenesis/experiments/L1_field/x168c_F26_g8_s965.compact.json) | other | 60606 | `ff0f0dd64414d5170032ba9a90de74a7e9f9e66dd9424b90fcdc923c56feebd3` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g10_s961.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g10_s961.compact.json) | other | 87591 | `6216a07ac66fae8ff610cfba5aa28315be8302e8f763dced04b09a83ea27dcfc` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g10_s962.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g10_s962.compact.json) | other | 75464 | `5aabc4fc2b3f226356d561cd423a79428d2175c01555caadd70ed9748e34fad1` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g10_s963.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g10_s963.compact.json) | other | 83351 | `b30a2f5a40c9bedc128bdf25277964196ee3a19f88775cdf83ac7a33c10e531a` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g10_s964.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g10_s964.compact.json) | other | 81454 | `12969504ddd3f4f946589b33f0d204b445bec924baad00fa232f6dfe3786438c` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g10_s965.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g10_s965.compact.json) | other | 76196 | `1641a602d15592139e9b30804ada81a4794a6c1a1027eeee32338f07d1aed139` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g11_s961.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g11_s961.compact.json) | other | 82399 | `92520a960074f5179cf9929e866207cb756c5394d84523150414481335259ae1` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g11_s962.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g11_s962.compact.json) | other | 67874 | `43b5f251d90eae7b445084a949b44b994820c7f31bbf6b21febded4100945c3e` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g11_s963.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g11_s963.compact.json) | other | 83968 | `cbeeb90784eca4e1ca8a2513863c03b6454aa79e8f2b83a2a7f5a6aed1eccc02` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g11_s964.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g11_s964.compact.json) | other | 80959 | `e298417e5b95a3cba18443bff8f36a4ddbba91f6cb2b0e4c68d11f23537bdc16` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g11_s965.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g11_s965.compact.json) | other | 79718 | `eb4c2d4e03d15e58ea2318dd72667dc135d36cb66670598205326949e644645d` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g8_s961.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g8_s961.compact.json) | other | 85485 | `7cca275cab0b4729429fb84a3c432366b8fa42c884635a5a6c3fd693be8629a3` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g8_s962.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g8_s962.compact.json) | other | 82599 | `3eb416ac5198d0fe78fda88339f52bbacf7bb8fa120d88d9ae96ce4a65fe5411` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g8_s963.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g8_s963.compact.json) | other | 83056 | `81f40a7135f344567b52b38a827f40127450ea6d48612ac6056f8240ffe7c00d` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g8_s964.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g8_s964.compact.json) | other | 76004 | `d661f845c6e2dcde09562655a7657295188bf8a5ffda6919583a56fb2324e108` |
| [`morphogenesis/experiments/L1_field/x168c_F30_g8_s965.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_g8_s965.compact.json) | other | 77509 | `528a5943fd6998ed84e0deacf43cc19968abb8e0c729efbb55d1ad3f3f963248` |
| [`morphogenesis/experiments/L1_field/x168c_F30_len_s961.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_len_s961.compact.json) | other | 576331 | `7637cc40891f7b0e4dd35c051f9d0b7670f03d50015473674df4c264998e5ab4` |
| [`morphogenesis/experiments/L1_field/x168c_F30_len_s962.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_len_s962.compact.json) | other | 532967 | `1428ae678def95c8a9b3a6a17fb8a674d13b01938e629fcb2d840da7730ffd0d` |
| [`morphogenesis/experiments/L1_field/x168c_F30_len_s963.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_len_s963.compact.json) | other | 511516 | `c9ccce939ae4f75ff4e0f022121df440bb16f4d651939156d78e18c4c43c52dc` |
| [`morphogenesis/experiments/L1_field/x168c_F30_len_s964.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_len_s964.compact.json) | other | 572313 | `3656fcb01408dd49162ee29fa9dd42f22df78e3942ed238d1949a02ad077540c` |
| [`morphogenesis/experiments/L1_field/x168c_F30_len_s965.compact.json`](../morphogenesis/experiments/L1_field/x168c_F30_len_s965.compact.json) | other | 545546 | `62caa812a5bdd3c4cc82221d3d56bc01817b522aaaa3d48a7bdedcd4b5f456cb` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g10_s961.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g10_s961.compact.json) | other | 72122 | `8a2a7c9cc2bc522ac3000db442ba117ac0113391646a4b0196236efc898296ac` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g10_s962.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g10_s962.compact.json) | other | 76180 | `61178d0b9cc7e857b043d7c66fb828ad59491311ba130ff21660c5b1d708420d` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g10_s963.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g10_s963.compact.json) | other | 72925 | `8bcee2a864e1c93c8d7ac2b695e874c6ee6523b3a3ec58ed1d284fe86f16b41e` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g10_s964.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g10_s964.compact.json) | other | 63934 | `82faa0f1afe181ef3cb29c89aafcadd3f5cb72214f96a3eb3f4b934dc0020d25` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g10_s965.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g10_s965.compact.json) | other | 68479 | `642fa60db657880cccf1b62619fc88c612f861d977a2443af2cc30343da3b57c` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g11_s961.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g11_s961.compact.json) | other | 63031 | `63149604e1777956bf2cb6f4d19ddd0e348f732ce341e25bb85f780e3aa812d6` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g11_s962.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g11_s962.compact.json) | other | 62839 | `d9b62ede0ca32b8716c669c56378173945167b547503e3db48a2261752bb5f33` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g11_s963.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g11_s963.compact.json) | other | 70714 | `8fd6ce8cac664b651242ea5304e32dad371513ab7e78d654c428c89cde24764d` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g11_s964.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g11_s964.compact.json) | other | 74444 | `a86df749d44d2d18cfb2c3cf93c72274464245121ec16ac97de04ad6af621264` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g11_s965.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g11_s965.compact.json) | other | 67890 | `0188f26224af83a7b0fe58c545431b34ca2ec21b1b42815adf18533189a6fdaf` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g8_s961.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g8_s961.compact.json) | other | 65665 | `ea4ad4862b8e7a628ed7b2792bddb5ef78c868df9838371166cced997c883ba5` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g8_s962.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g8_s962.compact.json) | other | 68311 | `0413e8cac2323f27c1241edd9b0f2258462f9a24cb651466d9ebb1d7a71e9616` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g8_s963.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g8_s963.compact.json) | other | 76570 | `f15638291f61518759bb8b3ad2e56398c7f3dd1833671e75f147921c0c875c30` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g8_s964.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g8_s964.compact.json) | other | 64116 | `fcb7894379f1abec0d609c9c61961b00f20b6c198df6ad12cb6c5396d3e42bf3` |
| [`morphogenesis/experiments/L1_field/x168c_F36_g8_s965.compact.json`](../morphogenesis/experiments/L1_field/x168c_F36_g8_s965.compact.json) | other | 68825 | `a423b0cd559b3a113df4ceb63970289ecb0839c52fd3dd8fca18689a74713f23` |
| [`morphogenesis/experiments/L1_field/x168c_series_index.json`](../morphogenesis/experiments/L1_field/x168c_series_index.json) | other | 7433 | `6a40c24d4d3e1d3b4da534cbcd0b3d5d2bbf709a131e5aab04f43a4ba03b09e8` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g11_s961.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g11_s961.compact.json) | other | 63396 | `e492e13385876811a5cdd94e1841adc8a6317e0ed931bc2100dc0bad8ee73e1a` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g11_s962.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g11_s962.compact.json) | other | 60295 | `ddeff67e55224c3c2bdcbeaf9612f156b9cf33b4319a4c7700b2ee9867a0fa54` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g11_s963.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g11_s963.compact.json) | other | 63561 | `b5d89705f595409ac17ade859a3b709712a3709281d0daa14bad97dc2ff36f19` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g11_s964.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g11_s964.compact.json) | other | 65345 | `53fdae79cfe6eb96aa316928a1fcc459c802a7aa1ef8537590203bc22c955d69` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g11_s965.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g11_s965.compact.json) | other | 64408 | `f895a013948d1daa3fc530ee6dfc5cb6b46c51a435faec850c5c26f6154fa707` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g11_s966.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g11_s966.compact.json) | other | 65309 | `c803f7fd372e3fbfb419a8410cd325d387ab3324a4f378129df27caf5a4e5bdd` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g11_s967.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g11_s967.compact.json) | other | 65159 | `63de0c84d0d71bbc55afe1425fa7a5f9f332869744bb78fc4a3b16ecb485ffc6` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g11_s968.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g11_s968.compact.json) | other | 65133 | `3526960a463e47351641b521b34e92fcb74ad890afc3f3136f44d5a174af5c79` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g11_s969.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g11_s969.compact.json) | other | 64798 | `07e60ab8e44986654e78770c6bd377cf781731792dd53c6cbf61325637d9c4f6` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g11_s970.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g11_s970.compact.json) | other | 62898 | `bf75dbccb5b5d877f657e38487e3ff30223e2616c1e0a4ea95788e0655165702` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g8_s961.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g8_s961.compact.json) | other | 65637 | `c71fe07cb012866f191fc3405c95096f23a426c17498780c2172168c7836d7a8` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g8_s962.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g8_s962.compact.json) | other | 61970 | `09139f45215fabeb710186f340da2393bcc128ccb1530826ab115d27ab7220a9` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g8_s963.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g8_s963.compact.json) | other | 62670 | `2643789ae6a0f9e7ba7861ee55abe9bfa2502f6111a473f9376335f1e3a0af5b` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g8_s964.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g8_s964.compact.json) | other | 62268 | `cac794067934c04c67c6f54e09535b86cbcf0ec896752e380a15d9f049d8db00` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g8_s965.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g8_s965.compact.json) | other | 60606 | `cc1b584f1e52c969828fb0261cf87e4bbb5e533e5247ad71c61f0f220a362d55` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g8_s966.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g8_s966.compact.json) | other | 60349 | `41c5fdc06d03fce2320b0df53fa245d1dc9534c4a8acc2668961d8d9a7e04cf4` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g8_s967.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g8_s967.compact.json) | other | 56862 | `005986e3d473151d82b8b498a233c74aa5271077fb7bee76fd8a94ea36ed1a24` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g8_s968.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g8_s968.compact.json) | other | 63864 | `195bb8c5b936a703b91ff95b593622a79f58355d61fa5ebe9bb7a096d62708b6` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g8_s969.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g8_s969.compact.json) | other | 64564 | `63e74bcebe3270559e37591579a3edce92e0ed7d4a9b072811af4c9fd9d54fd7` |
| [`morphogenesis/experiments/L1_field/x168d_F26_g8_s970.compact.json`](../morphogenesis/experiments/L1_field/x168d_F26_g8_s970.compact.json) | other | 61430 | `b0fd2ce003c5b29d4fd0c415347360167bda1d217a323323c1c2872a3921a496` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g11_s961.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g11_s961.compact.json) | other | 82399 | `e51b0811eae5ec8dce4c192cb239e17fd4902ad688405116a13504c9f9871963` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g11_s962.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g11_s962.compact.json) | other | 67874 | `32a0e4281c183ef77d9cd41bd00938a56a57e6d10367a34e4322cc6cef2083e0` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g11_s963.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g11_s963.compact.json) | other | 83968 | `4cc19d21765b677c35fa821900973c8560262534da304aef89a8c0e94d107c41` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g11_s964.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g11_s964.compact.json) | other | 80959 | `a1de124b168d058231b7e803c3c47ae14f220ab14c809d2c8c770a0ac8f689cb` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g11_s965.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g11_s965.compact.json) | other | 79718 | `94b4f45802f964c13b7c5f6cbf7a5a73d0470fdb76a82834fe34b8b9f0f8a61e` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g11_s966.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g11_s966.compact.json) | other | 82033 | `c788a78c5815e8ba6504332dfc5e15fe595dd0947362e3e031b4819f6c901f31` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g11_s967.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g11_s967.compact.json) | other | 75512 | `65c82511b34e49e8c5f2f6ed5b1e78094f5712967008b75ab55dc4cf625445f4` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g11_s968.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g11_s968.compact.json) | other | 83044 | `f4ee55a5d88180851b289e09e0cd803274c56fb70fc96c51e27dba011229cb2b` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g11_s969.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g11_s969.compact.json) | other | 79176 | `c71edf944bf093fea08a25307f1021a7aa56f1208e38d6f150efcf9ae122ba39` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g11_s970.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g11_s970.compact.json) | other | 77561 | `d9d19573abb01475c48a53a8fb1c3e9d17736ce882238815f4434291ef17d35b` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g8_s961.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g8_s961.compact.json) | other | 85485 | `cb3aec62fb78b0603025e70a0f9e5525a89b67f115bbb6d902585ce0a6a62db0` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g8_s962.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g8_s962.compact.json) | other | 82599 | `a4a4d93642b77def1495fe2f6841ac16677d6540bf8b78e4f68e5638887677f2` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g8_s963.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g8_s963.compact.json) | other | 83056 | `81af5acb0b02a2bd78f3adc08714f2cc6c265d78118a1d3bbfe5ca3bc5ab1c5f` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g8_s964.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g8_s964.compact.json) | other | 76004 | `4105b71007fb452e58eea35d1d887ab82abefdbdce091a16a5751753e0353137` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g8_s965.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g8_s965.compact.json) | other | 77509 | `1453a706fe8b7c729f6afe1c7921239f6872f680883db1ec464dd85652e807e4` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g8_s966.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g8_s966.compact.json) | other | 74853 | `e75dea74713237aa5c3195467a2ba91bb3fbb2849cc6fa0c0b483ba108e828e5` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g8_s967.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g8_s967.compact.json) | other | 82361 | `80f379cd5e0e23a5a75310d376fa499a6e81e6e626f72fbaff5e9768384cca2f` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g8_s968.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g8_s968.compact.json) | other | 81627 | `20417c039ec1b036cca72f1e1d99129ffc05000dc5887e16cbf771e866990f29` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g8_s969.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g8_s969.compact.json) | other | 78597 | `835ba8891f764daabc9edbb55907c5154ce50edbc469d2ccc28582bb2c6d48b9` |
| [`morphogenesis/experiments/L1_field/x168d_F30_g8_s970.compact.json`](../morphogenesis/experiments/L1_field/x168d_F30_g8_s970.compact.json) | other | 80772 | `6791424362e52581c1a516a96fc403f2d1f34a39bfa0f3132d2da110780d07d0` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g11_s961.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g11_s961.compact.json) | other | 63031 | `9fb060f09990c3e35dc408750c05eef03b573f11b37dc0c00760b36190374633` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g11_s962.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g11_s962.compact.json) | other | 62839 | `cc6be2bac2de4dd49a6ee4be13215a540dc1bc82220ee5a83d05e80d8b691618` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g11_s963.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g11_s963.compact.json) | other | 70714 | `f58ce74b6df64bbf49d6abdeab3cd5044357e825ae8eec07a9334cd5daa6bc5e` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g11_s964.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g11_s964.compact.json) | other | 74444 | `4b0d9defcc3030b6b6ce3261e589dd9c3a893154ddea7b6ff66d1aa42cdc2ee2` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g11_s965.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g11_s965.compact.json) | other | 67890 | `df6a5543a2e955809552058ebf5675b756c3358554a736d3d63c04fc551be65a` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g11_s966.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g11_s966.compact.json) | other | 69635 | `1c0f7ff8a281c820ddb9aca72ccdeb21871be885714d1d080dd89ef28a25ed3d` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g11_s967.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g11_s967.compact.json) | other | 76839 | `f9026e32687afc633a8c60b9d71e34604e503e106cd9ec1c77a6c282a436cb68` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g11_s968.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g11_s968.compact.json) | other | 68416 | `e2f3c16fe05f5003fefde85fa2778908f3621361df5e158da9a050052d18f0d6` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g11_s969.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g11_s969.compact.json) | other | 65853 | `21360f39bbc1c909da0e6857081075034a44635e3db333e6c9340368624720bc` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g11_s970.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g11_s970.compact.json) | other | 68907 | `dfe8cf978b0fa04ccdb1b343e1bdac86f74a236592b663fa697855e9f5ac2de0` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g8_s961.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g8_s961.compact.json) | other | 65665 | `26c9ec89672fab33dd8d83cdea0ff996f8265c03c71f8496f90ca3f4f406c0c7` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g8_s962.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g8_s962.compact.json) | other | 68311 | `30e7c189a4a4db178651851e0804fae33bd015d248521dc65e86143a4cfce3bf` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g8_s963.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g8_s963.compact.json) | other | 76570 | `531d995e41047697149a22ea981ffb2700d3fcd75697c623e0e656a0f8f9c72d` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g8_s964.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g8_s964.compact.json) | other | 64116 | `e7d4ef4a555a07599a21750e6b33081c7f2669ca28011d3c4b7f9c5158d229f6` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g8_s965.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g8_s965.compact.json) | other | 68825 | `0f89a2d9f3dbaf82a543dabd491c83782c7de8cce345111b570ed8006f5cc2ce` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g8_s966.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g8_s966.compact.json) | other | 71892 | `37bc46cefd7f3cbc63a72b5a4935d3224134808d1afcd1687a3315cedacce1e2` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g8_s967.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g8_s967.compact.json) | other | 74692 | `99733f5cf198dc6aacea374e11ecdd0311f516f4bec412fbdc6212fe3694865b` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g8_s968.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g8_s968.compact.json) | other | 75679 | `54e4ed4421eda36c5897f019598bbf7cce668593833751410c88bac9b45d8cf7` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g8_s969.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g8_s969.compact.json) | other | 73257 | `4d9108c9ead0e79839c30f95c046a797e4b82a4765231129621270c165543590` |
| [`morphogenesis/experiments/L1_field/x168d_F36_g8_s970.compact.json`](../morphogenesis/experiments/L1_field/x168d_F36_g8_s970.compact.json) | other | 73095 | `31f0fb2d91937e9852a6c499c4d73ea50b4865e43222332a54d79f037a3fbd1f` |
| [`morphogenesis/experiments/L1_field/x168d_series_index.json`](../morphogenesis/experiments/L1_field/x168d_series_index.json) | other | 7030 | `4712c9632633f1c7631dff1264d73c4657fd98f4c5644ba62838d0f0688041c5` |
| [`morphogenesis/experiments/L1_field/x169_pair_s991.compact.json`](../morphogenesis/experiments/L1_field/x169_pair_s991.compact.json) | other | 38887 | `76f2e5f631e55683b528f3c710f04ac89e5148d687dac36ccd020baa58a5f49b` |
| [`morphogenesis/experiments/L1_field/x169_pair_s992.compact.json`](../morphogenesis/experiments/L1_field/x169_pair_s992.compact.json) | other | 37722 | `6303da450d78a27d4aa1ad6b8d3fe52be5ad6cbae4d7da952ced8c3d946b83f6` |
| [`morphogenesis/experiments/L1_field/x169_pair_s993.compact.json`](../morphogenesis/experiments/L1_field/x169_pair_s993.compact.json) | other | 40028 | `109970b907ad6b61f2cf9b9afbd010b68fe2d8c84cfda36fd384d3e7514b82be` |
| [`morphogenesis/experiments/L1_field/x169_series_index.json`](../morphogenesis/experiments/L1_field/x169_series_index.json) | other | 754 | `8fe2c805f502216fca53772e3780ae636f86c3f0d2d746452ac8a0f838a7a885` |
| [`morphogenesis/experiments/L1_field/x169_single_s991.compact.json`](../morphogenesis/experiments/L1_field/x169_single_s991.compact.json) | other | 29385 | `332be7ef598fefffc0b45df985ba19dcec8d511a4f8ad8c0052e1b9241c9c96c` |
| [`morphogenesis/experiments/L1_field/x169_single_s992.compact.json`](../morphogenesis/experiments/L1_field/x169_single_s992.compact.json) | other | 26829 | `7f8f27dab7242f82e5b4bb190a42f95f185898c276eacccc85cba42676b1bf75` |
| [`morphogenesis/experiments/L1_field/x169_single_s993.compact.json`](../morphogenesis/experiments/L1_field/x169_single_s993.compact.json) | other | 26516 | `a85cde99d135eb593e13ab04a6b317d4cddaa1a27fe8d0b569e02dde1e84a04c` |
| [`morphogenesis/experiments/L1_field/x16_homog_s171.json`](../morphogenesis/experiments/L1_field/x16_homog_s171.json) | other | 4163 | `86096d9efbe672ae756bae7717453689ceb9b951ebe6da2d8dd1b1925cbe1261` |
| [`morphogenesis/experiments/L1_field/x16_homog_s172.json`](../morphogenesis/experiments/L1_field/x16_homog_s172.json) | other | 4572 | `ea5f04b990e4fe1782dec34b066f5b802b2148d49d7fa59820b55b3186b9d866` |
| [`morphogenesis/experiments/L1_field/x16_homog_s173.json`](../morphogenesis/experiments/L1_field/x16_homog_s173.json) | other | 4618 | `2953bff6b7cd03ca9b4eb607d7eae3b5d3e9aa100b3a9b4841e02ae65a27195b` |
| [`morphogenesis/experiments/L1_field/x16_homog_s174.json`](../morphogenesis/experiments/L1_field/x16_homog_s174.json) | other | 4255 | `5f49035baa7ff5a4097ae3b41757272d526aad1bff8e78c94d9e10e346c82d59` |
| [`morphogenesis/experiments/L1_field/x16_homog_s175.json`](../morphogenesis/experiments/L1_field/x16_homog_s175.json) | other | 4307 | `d671472a0a0e324fdc4e343b050a5071cb2cc09fa2ce085618b1f8991030736f` |
| [`morphogenesis/experiments/L1_field/x16_homog_s176.json`](../morphogenesis/experiments/L1_field/x16_homog_s176.json) | other | 4555 | `b6d01d57b1eb520fdbe155edbe2723ad8022cff4f03d0f04ba2ae07ac68733e2` |
| [`morphogenesis/experiments/L1_field/x16_homog_s177.json`](../morphogenesis/experiments/L1_field/x16_homog_s177.json) | other | 4176 | `593740486f769db10e6247725813746b253711e65b3972dfb74188744601d384` |
| [`morphogenesis/experiments/L1_field/x16_homog_s178.json`](../morphogenesis/experiments/L1_field/x16_homog_s178.json) | other | 4282 | `e5af1ad44186724da996f12b1bc44200940d0e3bef958516ecf195b6b5d3fff1` |
| [`morphogenesis/experiments/L1_field/x16_homog_s179.json`](../morphogenesis/experiments/L1_field/x16_homog_s179.json) | other | 4180 | `2a97a291c03a259011618923af335855e5e7e85e2d6a403cbed4e23cc7ed5cc0` |
| [`morphogenesis/experiments/L1_field/x16_homog_s180.json`](../morphogenesis/experiments/L1_field/x16_homog_s180.json) | other | 4258 | `ad5def042a8c203ea42ef0e8dcf6e75c1b74e96aac0e483c48f7408f646736a3` |
| [`morphogenesis/experiments/L1_field/x16_homog_s181.json`](../morphogenesis/experiments/L1_field/x16_homog_s181.json) | other | 4305 | `a3d17368037a48039f009c939bb1cef471c6f1c553ae0d02cbcda4efe60ef9e8` |
| [`morphogenesis/experiments/L1_field/x16_homog_s182.json`](../morphogenesis/experiments/L1_field/x16_homog_s182.json) | other | 4276 | `5e70bc9bf3f7dc8cc2e0caf68a0aa1de9e931d8b03d0aaebcc23ce77e442eca4` |
| [`morphogenesis/experiments/L1_field/x16_homog_s183.json`](../morphogenesis/experiments/L1_field/x16_homog_s183.json) | other | 4132 | `c4cb006b21ae3a9c185145f787b3ec3192581f9bc5fe5cd72325718ca0555165` |
| [`morphogenesis/experiments/L1_field/x16_homog_s184.json`](../morphogenesis/experiments/L1_field/x16_homog_s184.json) | other | 4193 | `a11382be0feb9f2a9d9a9fc77f6f887be3f202325039d3298513671e19b75c84` |
| [`morphogenesis/experiments/L1_field/x16_homog_s185.json`](../morphogenesis/experiments/L1_field/x16_homog_s185.json) | other | 4150 | `fb3c612a4aab0d57f748bc0a327e3d2edf618f4cf76828803aea403aa3045524` |
| [`morphogenesis/experiments/L1_field/x16_homog_s186.json`](../morphogenesis/experiments/L1_field/x16_homog_s186.json) | other | 4415 | `e352c5840dff7ffc24943803ed721da7298dcfab28e6d4dadb2fb24f6b72ac78` |
| [`morphogenesis/experiments/L1_field/x16_homog_s187.json`](../morphogenesis/experiments/L1_field/x16_homog_s187.json) | other | 4295 | `d0a355067788e3e75de05dfb0d4303721123a66a5e5029b8eeb494537038696e` |
| [`morphogenesis/experiments/L1_field/x16_homog_s188.json`](../morphogenesis/experiments/L1_field/x16_homog_s188.json) | other | 4322 | `fab837417f13ff0c0f0e5294e097bab05ebe61962ca99bbd372429ed3a95d339` |
| [`morphogenesis/experiments/L1_field/x16_homog_s189.json`](../morphogenesis/experiments/L1_field/x16_homog_s189.json) | other | 4267 | `5aa1fd238b58e52fa931410e6969c8c9b98a3f79c4cbf3f01e3daf5c79ad1c31` |
| [`morphogenesis/experiments/L1_field/x16_homog_s190.json`](../morphogenesis/experiments/L1_field/x16_homog_s190.json) | other | 4206 | `943f7affcb8cc07d6af53315b81b139a67eb74d22493e0fbb2eb72af737fdc75` |
| [`morphogenesis/experiments/L1_field/x16_static_s171.json`](../morphogenesis/experiments/L1_field/x16_static_s171.json) | other | 4619 | `50f2eaad45546ce8a69e396fe138688a2868640f349e9753a41fa6647e1535be` |
| [`morphogenesis/experiments/L1_field/x16_static_s172.json`](../morphogenesis/experiments/L1_field/x16_static_s172.json) | other | 4409 | `f4a097d41af63e00d9302e196d41f113d0867736d0bf0654019d8658ab43961c` |
| [`morphogenesis/experiments/L1_field/x16_static_s173.json`](../morphogenesis/experiments/L1_field/x16_static_s173.json) | other | 4994 | `03c7c81233cee9f3c0ecb49fed7c1f0a0425fb84dfa8297092e6892e195bb43f` |
| [`morphogenesis/experiments/L1_field/x16_static_s174.json`](../morphogenesis/experiments/L1_field/x16_static_s174.json) | other | 4419 | `d1c371afa8f4c71f5a09b9928dd5f9938fe4042c0f6b4a5c8aac38bbcc7f54ec` |
| [`morphogenesis/experiments/L1_field/x16_static_s175.json`](../morphogenesis/experiments/L1_field/x16_static_s175.json) | other | 4952 | `3a8b0f12064e604e085259cbfb6f6f4412543e5162895f6a079decb7ed553e4c` |
| [`morphogenesis/experiments/L1_field/x16_static_s176.json`](../morphogenesis/experiments/L1_field/x16_static_s176.json) | other | 4639 | `01d271fc828ecb93382c7a04f410098dac1e44c708765de5e7a2e76321ad0d36` |
| [`morphogenesis/experiments/L1_field/x16_static_s177.json`](../morphogenesis/experiments/L1_field/x16_static_s177.json) | other | 4876 | `c37d64c06dab8369dc48669400389c9f841843d090de85692afb7b31d663ddd2` |
| [`morphogenesis/experiments/L1_field/x16_static_s178.json`](../morphogenesis/experiments/L1_field/x16_static_s178.json) | other | 4304 | `66c6381cd807a81c3d580fc91a0f174d8cacbff3bc87d7efc2c2056aa269c3d7` |
| [`morphogenesis/experiments/L1_field/x16_static_s179.json`](../morphogenesis/experiments/L1_field/x16_static_s179.json) | other | 4321 | `c2b1c31efdae28112d420476a8c8fe28146d51fa3cd927c229db4b8e64057c90` |
| [`morphogenesis/experiments/L1_field/x16_static_s180.json`](../morphogenesis/experiments/L1_field/x16_static_s180.json) | other | 4406 | `5767008ac5456f8e963dd50000338c4209d4d6e6bef6c183e8e18fd105e03e9c` |
| [`morphogenesis/experiments/L1_field/x16_static_s181.json`](../morphogenesis/experiments/L1_field/x16_static_s181.json) | other | 5021 | `39518ab2f40ac6ab83b29be3b5bae65a7162a4ea5cb0f4bc3e6beb9d401c40f8` |
| [`morphogenesis/experiments/L1_field/x16_static_s182.json`](../morphogenesis/experiments/L1_field/x16_static_s182.json) | other | 5745 | `65a87fd14c150b9bdfc93d7b897d07fc467e43786a4a786f850d0a6ee54d891a` |
| [`morphogenesis/experiments/L1_field/x16_static_s183.json`](../morphogenesis/experiments/L1_field/x16_static_s183.json) | other | 4258 | `19d222568fd852474af7f74d0add6ea470a134ab733539e7907ad96de623fbc4` |
| [`morphogenesis/experiments/L1_field/x16_static_s184.json`](../morphogenesis/experiments/L1_field/x16_static_s184.json) | other | 4579 | `5dffd57db4b05a3caaab161c3a4401f8c18135149284b6dfe72da0ad902ae91b` |
| [`morphogenesis/experiments/L1_field/x16_static_s185.json`](../morphogenesis/experiments/L1_field/x16_static_s185.json) | other | 4274 | `47f4618d06800db7b2a676d25f0ef4d25a20a7e084093f09146d4aabe5fe8a98` |
| [`morphogenesis/experiments/L1_field/x16_static_s186.json`](../morphogenesis/experiments/L1_field/x16_static_s186.json) | other | 4301 | `ee13a35d924743159a33392bb9251ebd5e11581a52ba603f8dd8fef947ae5925` |
| [`morphogenesis/experiments/L1_field/x16_static_s187.json`](../morphogenesis/experiments/L1_field/x16_static_s187.json) | other | 5827 | `ee63de22053ab979ba697e52701bffc362c2a159856337c625cc01584b89a146` |
| [`morphogenesis/experiments/L1_field/x16_static_s188.json`](../morphogenesis/experiments/L1_field/x16_static_s188.json) | other | 4365 | `de3233fe1ed58359453582a74ca115da59f69ed98669d46a3e0fac3122bb8d83` |
| [`morphogenesis/experiments/L1_field/x16_static_s189.json`](../morphogenesis/experiments/L1_field/x16_static_s189.json) | other | 5105 | `8d01450eb57b679d1b3f85bc126b28519946d036c791a1325c3d8af3648bfb02` |
| [`morphogenesis/experiments/L1_field/x16_static_s190.json`](../morphogenesis/experiments/L1_field/x16_static_s190.json) | other | 4243 | `8551b202b00715501836a05a4933cfca8ebc16072b2d0aa67540fa00ff09d6c1` |
| [`morphogenesis/experiments/L1_field/x170_F26_s971.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s971.compact.json) | other | 62129 | `b61fbcf94bf870bea4889a201d751aa9037ced9624fe6490c3bf74b15789050b` |
| [`morphogenesis/experiments/L1_field/x170_F26_s972.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s972.compact.json) | other | 65194 | `84f58058807f5922e4bffd89f1007116da77eb82c081e15c9f4903c4dce43054` |
| [`morphogenesis/experiments/L1_field/x170_F26_s973.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s973.compact.json) | other | 61952 | `859a8901ea4b63114e2a48492c897cb37b7447a2e72c544bbcea8f4de9073cc1` |
| [`morphogenesis/experiments/L1_field/x170_F26_s974.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s974.compact.json) | other | 63311 | `9b4facd717815be2e4c309c300e774d75f6605671d90d83064129228de48b059` |
| [`morphogenesis/experiments/L1_field/x170_F26_s975.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s975.compact.json) | other | 63302 | `272effcdec095d86970f1c12ccd631c08302b127a5b58928bc5bc1d91512db27` |
| [`morphogenesis/experiments/L1_field/x170_F26_s976.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s976.compact.json) | other | 67734 | `72a8e4f32038f0d5ff733be676cbf35aceb13848caada82f437db9d37b576daa` |
| [`morphogenesis/experiments/L1_field/x170_F26_s977.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s977.compact.json) | other | 67116 | `5c79a91553e0cd4f2dec4de5673476d1aa2737f0b7a915d7622b1af4fad32435` |
| [`morphogenesis/experiments/L1_field/x170_F26_s978.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s978.compact.json) | other | 62184 | `4eca8e6b87fd3269a9962087cb4a0aa68d62d0c13934155696742c31f9277bb7` |
| [`morphogenesis/experiments/L1_field/x170_F26_s979.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s979.compact.json) | other | 62029 | `85f7c8a14859b6fe51feb64b64268243535e2bb16b68e126e338f4db639076a5` |
| [`morphogenesis/experiments/L1_field/x170_F26_s980.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s980.compact.json) | other | 62623 | `fc812d8c24d72a908233e64bf5d546b30068fda77c304b2206d4d60a30dca071` |
| [`morphogenesis/experiments/L1_field/x170_F26_s981.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s981.compact.json) | other | 65700 | `ee9ad3706788e08523b37f45d0061ddab0668d897c777eab223dd846ccb4b1ad` |
| [`morphogenesis/experiments/L1_field/x170_F26_s982.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s982.compact.json) | other | 64956 | `d9ac0e779773f7b3bcc156fe54027dc2835d2904e238a6a8c34547b2cdda4189` |
| [`morphogenesis/experiments/L1_field/x170_F26_s983.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s983.compact.json) | other | 64332 | `0556a0ee6c6db21b525c96472b17ecb50aa7f3632bd438e5fe0fa6b8a23b26a4` |
| [`morphogenesis/experiments/L1_field/x170_F26_s984.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s984.compact.json) | other | 64800 | `e19344d62920d697580b833123918bafe8cfeb36fb53745095aac5e84826f875` |
| [`morphogenesis/experiments/L1_field/x170_F26_s985.compact.json`](../morphogenesis/experiments/L1_field/x170_F26_s985.compact.json) | other | 63431 | `d7183e0bb5923446f844ecc9506ce958f9c34eacf74bd716663ec13c897330bf` |
| [`morphogenesis/experiments/L1_field/x170_F30_s971.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s971.compact.json) | other | 68039 | `9323d26ceb46fd3b1a086273ab5979841b5edecf3567fb6c7fb5a313b517cd81` |
| [`morphogenesis/experiments/L1_field/x170_F30_s972.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s972.compact.json) | other | 81467 | `73664f12df99cf1e9345f1482928f4b967a6b60bd3247a11db8a77bc4c2a7cbd` |
| [`morphogenesis/experiments/L1_field/x170_F30_s973.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s973.compact.json) | other | 77761 | `413950f75c924ef83a3ae7c44ef2ddd160a15f76a52fe0c60cf1ac5c8f900218` |
| [`morphogenesis/experiments/L1_field/x170_F30_s974.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s974.compact.json) | other | 81099 | `63d2ee5aac1918aa61e14478855ae82cfe388a5554e26a5485f2d36105d81c88` |
| [`morphogenesis/experiments/L1_field/x170_F30_s975.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s975.compact.json) | other | 87673 | `df1f18feffd92eb9b9920f9a7e9855090f6f753ed13f4f7fcc7f2d5357d2b22d` |
| [`morphogenesis/experiments/L1_field/x170_F30_s976.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s976.compact.json) | other | 81556 | `3c3c413f383273ff3b429950093683fd98c737d92b67f1408281e07de7645cb6` |
| [`morphogenesis/experiments/L1_field/x170_F30_s977.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s977.compact.json) | other | 81030 | `3795d7887034b5308f5f65b8eb5959aebecc5f6ad84ffacdea77b21741eef9c8` |
| [`morphogenesis/experiments/L1_field/x170_F30_s978.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s978.compact.json) | other | 77186 | `d220874e32d64e3449735cc2d2ff0239b40bf920bff5fd8697b930f0abd95489` |
| [`morphogenesis/experiments/L1_field/x170_F30_s979.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s979.compact.json) | other | 77761 | `c6929530ef0b0c6aa4b58f5ae8b46dd040d846fadb272a719583a523ca0e43d2` |
| [`morphogenesis/experiments/L1_field/x170_F30_s980.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s980.compact.json) | other | 88870 | `2d7d6e4a5f199a98d6054af85e65390eb2caa1b45c533a6b0c31442ab8b12cd8` |
| [`morphogenesis/experiments/L1_field/x170_F30_s981.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s981.compact.json) | other | 78888 | `9d1e29947ad8351bd7033cacb855e6ce921a0c9e77bc527c24c3a978cda2629e` |
| [`morphogenesis/experiments/L1_field/x170_F30_s982.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s982.compact.json) | other | 81454 | `b8386ea47e552d38ebca516e58c7a149705444d8d3179256587a9e1cc4f630bd` |
| [`morphogenesis/experiments/L1_field/x170_F30_s983.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s983.compact.json) | other | 86581 | `934dd3a10fdb6ca8c4d7767639e93482207f3ab3b44889573e0fa28ded08bde7` |
| [`morphogenesis/experiments/L1_field/x170_F30_s984.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s984.compact.json) | other | 76216 | `e2c98fed2a782f14750e532b8b0ab1cb78bc8f3f7e11187d9a5489be6643e7fb` |
| [`morphogenesis/experiments/L1_field/x170_F30_s985.compact.json`](../morphogenesis/experiments/L1_field/x170_F30_s985.compact.json) | other | 81233 | `cdb6ab37d58b2c24adc1f552f3bba12527d3dd9d1f94bf3219c863f4145feee0` |
| [`morphogenesis/experiments/L1_field/x170_F36_s971.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s971.compact.json) | other | 70561 | `5c7ccfbfef54ffe3d4003761bfb47ac66321b22f12c8aabc1befd00a2ee423d0` |
| [`morphogenesis/experiments/L1_field/x170_F36_s972.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s972.compact.json) | other | 70738 | `48f82b7e34f41467bf1457fa7c329fd03f5e5ece5232a652042f6e607a1dec11` |
| [`morphogenesis/experiments/L1_field/x170_F36_s973.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s973.compact.json) | other | 64959 | `5af1eae3267522a596b558f8bde991eb2c36a81aada13c2e7bcf4208859b2396` |
| [`morphogenesis/experiments/L1_field/x170_F36_s974.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s974.compact.json) | other | 74436 | `2532ce6bf7fd58c2a3dbf270eda78efe4148fedb62866b283eedd30eed374d90` |
| [`morphogenesis/experiments/L1_field/x170_F36_s975.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s975.compact.json) | other | 72066 | `4a73fd073dc71e44affcf0d3f4e42b3c510475d355937827ae99f2350e337aa3` |
| [`morphogenesis/experiments/L1_field/x170_F36_s976.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s976.compact.json) | other | 64021 | `1ae166a332d55683d73b87449264d506b7543e4a0cecbe175d47b61208d6205b` |
| [`morphogenesis/experiments/L1_field/x170_F36_s977.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s977.compact.json) | other | 63567 | `566ee57095d134fd16cfff89e72d354cd879bbb05a594cab2d7db56aea619d36` |
| [`morphogenesis/experiments/L1_field/x170_F36_s978.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s978.compact.json) | other | 64924 | `aea6e2734569c1fee6e2c8c25f94b7d5a05eaf0393b8c77f334f16004b284df7` |
| [`morphogenesis/experiments/L1_field/x170_F36_s979.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s979.compact.json) | other | 65007 | `72915c49039be35ee914d89feeceee073c9d3041b88bc329d5506fdd8df8f193` |
| [`morphogenesis/experiments/L1_field/x170_F36_s980.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s980.compact.json) | other | 65825 | `80343f8d11d5d67f245685a79afc322032a81b3d564cf8159903ae8d521fd0eb` |
| [`morphogenesis/experiments/L1_field/x170_F36_s981.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s981.compact.json) | other | 61456 | `4fbf69141e92650994d35dbf2b93f9b34a66a5d185ed60943d3447f0ef4375ad` |
| [`morphogenesis/experiments/L1_field/x170_F36_s982.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s982.compact.json) | other | 73034 | `d20fc7752656613432177f03c1c5eadb7e9e5f6036667736888c2a11d53e115b` |
| [`morphogenesis/experiments/L1_field/x170_F36_s983.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s983.compact.json) | other | 61370 | `bbb5b3a3421b1ccb4bb11336536711a23c0dcc17e709fe27072788c1c26472f4` |
| [`morphogenesis/experiments/L1_field/x170_F36_s984.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s984.compact.json) | other | 68528 | `daf78efc3624541d115855ab36e4df475da644514c25a3580362fd2d0b904fba` |
| [`morphogenesis/experiments/L1_field/x170_F36_s985.compact.json`](../morphogenesis/experiments/L1_field/x170_F36_s985.compact.json) | other | 74328 | `501cec72d7714cb8af7973f1f340a05f940351a0266d63e3c8bfb8907606f22f` |
| [`morphogenesis/experiments/L1_field/x170_series_index.json`](../morphogenesis/experiments/L1_field/x170_series_index.json) | other | 4408 | `8bfeaeaaba4439573d6dde3e50edcbb194277c0a918608314043815b707d7c47` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s971.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s971.compact.json) | other | 82055 | `f86372a923b38b9f6d501ada6de3f6896b1644ff60bbb9148bc03bb18f01f126` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s972.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s972.compact.json) | other | 87626 | `8a4293ee2a53c6f4206628e6c3c243f35244daddf4bf936651a3f52bc5158bab` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s973.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s973.compact.json) | other | 83682 | `91c1a2c0c6e2d53e22f5ab94d4c8587f261ac2bd79bd05c86ce2ede24281269a` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s974.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s974.compact.json) | other | 84295 | `d4bfbe754215672b2df2b15df1edae21bb048233a3a4e8322b12fc877bb4e974` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s975.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s975.compact.json) | other | 88513 | `725477bb415185872968d222e6e6cf2d4fce11b12faea26d11d6c0e35b69255b` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s976.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s976.compact.json) | other | 90859 | `260344ece25f8d532fd064e2c497358776faf9c491cc2123cced71f90d1f6398` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s977.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s977.compact.json) | other | 90070 | `233f6d714e720066a7a528a991bb7c09b7e561fee89e2d8c7689536e8cf78fb5` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s978.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s978.compact.json) | other | 92130 | `3df9c10e0bc47ccbb68ab6a4dc08c2bfaa90312a38c7258ea73e09f8e8ec05f1` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s979.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s979.compact.json) | other | 83883 | `860760f2b80452377e16cca91c239fe083b1457a3b49c4d6345d1623c9c9b67e` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s980.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s980.compact.json) | other | 81191 | `4653b1d5a73b78ee222e4000f86fac6f3365bc59836a0127b084a4de24443087` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s981.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s981.compact.json) | other | 87342 | `5e05b22f8f98a8e2174c59748e49967086b696898854e100c883d81b82ee5eb9` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s982.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s982.compact.json) | other | 84233 | `0874a55b2c82635ebe00225a446dcb6aebd56e6f0b0e2ee12df669f1d79dd40c` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s983.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s983.compact.json) | other | 89930 | `9011e8b85b1449a5be3e4b9cccc2b8675daafda6eef796634127fd875273e3d1` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s984.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s984.compact.json) | other | 83442 | `bb9e684d35c25b01cb185fae70668b667ccc87693a65120e59667719dc396989` |
| [`morphogenesis/experiments/L1_field/x171_r4.5_g10_s985.compact.json`](../morphogenesis/experiments/L1_field/x171_r4.5_g10_s985.compact.json) | other | 84422 | `294c0f0c7a4758da5724784d986335ba7f9f2794a3e3b7060eabd722ec6ce4df` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s971.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s971.compact.json) | other | 85057 | `1f3ae5f6a04b5d42cf7c702b073a00aff25aa682bd8f37fc00c2293839ccae3f` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s972.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s972.compact.json) | other | 88102 | `1e9460cfb6ed4d2e4bd5cd6cea1650bcc566f4c162263f395761d68a17440d6a` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s973.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s973.compact.json) | other | 90505 | `275d053c44e203c7157cdb8e5d80336e88122aa411a53ad5d5402f2b1725dc35` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s974.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s974.compact.json) | other | 91136 | `a1a550e91393dd04ebf69aaae592ae67b2c5cb2d68cdec75599bc8356e2c14fc` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s975.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s975.compact.json) | other | 90291 | `01253ff641427a4fa2a63872abe7e13c96255f24abc4448edd986fedad0b1739` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s976.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s976.compact.json) | other | 85536 | `ba8c77955c867156c9bd7ac030501a4891cf8146ac16f8a8ae20312d6915982d` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s977.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s977.compact.json) | other | 84950 | `13dd951000b1a8c208ac254b3014f531165c3bce30e5eae28eac4f0ef46886ef` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s978.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s978.compact.json) | other | 94291 | `91ec2cee7aa19c2bb9fed6fc0b9f98e1fbe1849b70b052ed00ec8addf9c6a43d` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s979.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s979.compact.json) | other | 90912 | `35f56da72d476e9a4c6093c763dfbb5f4e45f0ab06c4ebf1258c52ae10f55e6d` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s980.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s980.compact.json) | other | 88270 | `1f2174d9b81490f077b3387c6efb68b8eee18327917feb113580fa8acbbc40da` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s981.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s981.compact.json) | other | 89947 | `8d1155bd025fc114ce134f471280bdcab57660b64ea8dfc0bc33df954eaf7af0` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s982.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s982.compact.json) | other | 93630 | `958257a579175cbaa1c6ef6f7607499dfe6c934094984b775821aca354f90238` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s983.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s983.compact.json) | other | 86935 | `6b4d7e3fba4fadce31abcdb1ffbbaf5f49dae7b1a31fec700fe4e3ed55688c08` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s984.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s984.compact.json) | other | 96170 | `7fc24ae0edb19405432954a15f9efd0a1cc67ec86d9903a4d56c9a0c0e04b6aa` |
| [`morphogenesis/experiments/L1_field/x171_r6_g9_s985.compact.json`](../morphogenesis/experiments/L1_field/x171_r6_g9_s985.compact.json) | other | 91167 | `72b7029aaf2d65e68d399820b2bbd19482a59584d4d6e34861e41378a7b18acb` |
| [`morphogenesis/experiments/L1_field/x171_series_index.json`](../morphogenesis/experiments/L1_field/x171_series_index.json) | other | 3673 | `5ed92a29ba045ac7a6184a641d2ecc415abdea1d7983fdba20eb8fa4ac286809` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s1000.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s1000.compact.json) | other | 81849 | `bc39d5fab924ce6b6a75eaa4ec4781f050ee7ab612d73ac1b985cea3954ea9d5` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s1001.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s1001.compact.json) | other | 81618 | `4f2ce7f122e1b63c2107f244fc6d1182a7d7be0b57b09971f0ed9caf0fb43de8` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s1002.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s1002.compact.json) | other | 94387 | `974589f0d0c147d05974a443d536529251f7231cd4cdbdcdf620d35b6e01aeab` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s1003.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s1003.compact.json) | other | 62685 | `128b14bf4bf634e5608f2bed64eac9030d27f1a72cdccaf1caa9e6b6922fc6a9` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s1004.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s1004.compact.json) | other | 81966 | `578f54dbf858cd077b52a369c5f9a458374f187ee26f9d67c23d23d33fd15a36` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s1005.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s1005.compact.json) | other | 86486 | `c5decf6d51577a88a9daa8449eff4d4a38892b8ff5721f3632d860040854c050` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s986.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s986.compact.json) | other | 87696 | `369760b883b46de5345f7b28dedbfa3174ac501c15b755db49f191334db1e114` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s987.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s987.compact.json) | other | 78639 | `d1d6024c034c196d1842999048c0bdba36961b8e421c13c7e0473b9bf4cebab9` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s988.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s988.compact.json) | other | 69083 | `07b7704adc576b02e18a9d9c57e5f3f74379f16f12a936e1112a1944d533305e` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s989.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s989.compact.json) | other | 94367 | `b91219eabb0cd9418d98e0d7c7c5a88c28178a89e8c8132cb0d3ea2ed22cb617` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s990.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s990.compact.json) | other | 94296 | `40c318810ab6cc5445715a8727d7c4934e78ea87fd38c9d7564ce6d6d2ee2145` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s991.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s991.compact.json) | other | 84017 | `7351e4dfae308f7702d3f7838e941a4401d16d1f3d43edeec9221800e6eac073` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s992.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s992.compact.json) | other | 76112 | `6ca2584d38b39cf6f7ddaf293c5ab004d295d6ead86f3d5d1aa8ebf0a6edac00` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s993.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s993.compact.json) | other | 83151 | `3aa4d4fa7535f0f3c5e13c4ad757458311186f7332fde24d65cbd023eabc52cc` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s994.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s994.compact.json) | other | 78625 | `fb3c17151c7d94572f449cbbca27e12def12fccd005b3a1ce4c0405956ac50b6` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s995.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s995.compact.json) | other | 81807 | `b60dcac8d158c58659a981f8924dfd56ac8f8978822a166b9f4fe07d81d462ab` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s996.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s996.compact.json) | other | 86356 | `35f601c4cc09dc5914165d8d8a80f5d5ad00bd1b0f3ff9070484024e2ac57303` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s997.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s997.compact.json) | other | 82686 | `7523348d1a489b4a994887899ccad6d6f0f35be6e168d2c5fc2fef0d4078e064` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s998.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s998.compact.json) | other | 82512 | `6ab49dba3bd7ccacab131e9479ddfaa484e2e6262808b1d49c63a91bf27427e1` |
| [`morphogenesis/experiments/L1_field/x172_gap10_s999.compact.json`](../morphogenesis/experiments/L1_field/x172_gap10_s999.compact.json) | other | 87391 | `df8a72acd96efa9197cd04374d8c618b7d43c5f1634a264067a9c2df113a02ba` |
| [`morphogenesis/experiments/L1_field/x172_gap8_s986.compact.json`](../morphogenesis/experiments/L1_field/x172_gap8_s986.compact.json) | other | 84481 | `45d9c1fc68315b972b7ebd48263d563118ec8e3bbe0b17e0d9a7e5ee96e61755` |
| [`morphogenesis/experiments/L1_field/x172_gap8_s987.compact.json`](../morphogenesis/experiments/L1_field/x172_gap8_s987.compact.json) | other | 77519 | `e94c5c6113f3e65961ed580fffdd4a3185449692fbbe021fee9efbfcf35ce9f4` |
| [`morphogenesis/experiments/L1_field/x172_gap8_s988.compact.json`](../morphogenesis/experiments/L1_field/x172_gap8_s988.compact.json) | other | 82996 | `d898c6d09781b7d2827e21f0fea767d3c0ecd17f2eea7359c212588a9184423c` |
| [`morphogenesis/experiments/L1_field/x172_gap8_s989.compact.json`](../morphogenesis/experiments/L1_field/x172_gap8_s989.compact.json) | other | 80861 | `4e9d4f8dfa2b6569ca58abe29501b5263f0a19751d5842353a34f70601cbe16f` |
| [`morphogenesis/experiments/L1_field/x172_gap8_s990.compact.json`](../morphogenesis/experiments/L1_field/x172_gap8_s990.compact.json) | other | 80929 | `40cebe1e02ab7b537c9c1512ed5d84741171c665587577a44d019993f8a6b116` |
| [`morphogenesis/experiments/L1_field/x172_series_index.json`](../morphogenesis/experiments/L1_field/x172_series_index.json) | other | 2908 | `2a69a178338008b0862bde1ec61adb29df8bfacd7fad6e08dec1160020436544` |
| [`morphogenesis/experiments/L1_field/x173_g10_s1011.compact.json`](../morphogenesis/experiments/L1_field/x173_g10_s1011.compact.json) | other | 183196 | `131a342d0a590a3d0e08581b94dd724bf3535f9f75a03d89da994388774f1f48` |
| [`morphogenesis/experiments/L1_field/x173_g10_s1012.compact.json`](../morphogenesis/experiments/L1_field/x173_g10_s1012.compact.json) | other | 203445 | `2d0d1e44aa8d63efb44f217f2730808bd99000fd13b47e1ddee0cff3587430af` |
| [`morphogenesis/experiments/L1_field/x173_g10_s1013.compact.json`](../morphogenesis/experiments/L1_field/x173_g10_s1013.compact.json) | other | 186212 | `27f27af717ed330e98f65d07ce047462e80d763bef965901b8ae373a4036c0a8` |
| [`morphogenesis/experiments/L1_field/x173_g10_s1014.compact.json`](../morphogenesis/experiments/L1_field/x173_g10_s1014.compact.json) | other | 187388 | `cdaf6cf148331ab98f45b7411bc4af31e2277a00b52885823246975e2afbc795` |
| [`morphogenesis/experiments/L1_field/x173_g10_s1015.compact.json`](../morphogenesis/experiments/L1_field/x173_g10_s1015.compact.json) | other | 196445 | `72abc3280ee0f031b2864cdcb585a0763829bc791007315724613c57662c1206` |
| [`morphogenesis/experiments/L1_field/x173_g10_s1016.compact.json`](../morphogenesis/experiments/L1_field/x173_g10_s1016.compact.json) | other | 192221 | `15c9d4ee469cc5a627aacc105e7b9af7f258fd237f9884e14f1c934559c3a8ab` |
| [`morphogenesis/experiments/L1_field/x173_g10_s1017.compact.json`](../morphogenesis/experiments/L1_field/x173_g10_s1017.compact.json) | other | 192947 | `bc07760eff4b89a41662601c3210aa9f1af9b0a6e30a2ba733f02c978ba31348` |
| [`morphogenesis/experiments/L1_field/x173_g10_s1018.compact.json`](../morphogenesis/experiments/L1_field/x173_g10_s1018.compact.json) | other | 186213 | `8e60cd2b2f6e60920bdff7ed56f95118ee60e454aaf366c307c9fd21703b3177` |
| [`morphogenesis/experiments/L1_field/x173_g10_s1019.compact.json`](../morphogenesis/experiments/L1_field/x173_g10_s1019.compact.json) | other | 196777 | `23c1afb0cd5d641535ed4112b9d9273435076aa33840190bf7f531de77306f5c` |
| [`morphogenesis/experiments/L1_field/x173_g10_s1020.compact.json`](../morphogenesis/experiments/L1_field/x173_g10_s1020.compact.json) | other | 184567 | `beab0e4e345fb0207ef8568aa113e9f249d4fb104617c862a104ac18fa23569b` |
| [`morphogenesis/experiments/L1_field/x173_g11_s1011.compact.json`](../morphogenesis/experiments/L1_field/x173_g11_s1011.compact.json) | other | 192481 | `4cf6016e3aa2ffcc2d31691ab66f3bcb724e11ee96b0d90763e77620b00b7c0e` |
| [`morphogenesis/experiments/L1_field/x173_g11_s1012.compact.json`](../morphogenesis/experiments/L1_field/x173_g11_s1012.compact.json) | other | 184879 | `98e8d1495f33fedd996c2338662f44f1a61020d55442c8e3444f3a184b4c8c38` |
| [`morphogenesis/experiments/L1_field/x173_g11_s1013.compact.json`](../morphogenesis/experiments/L1_field/x173_g11_s1013.compact.json) | other | 181868 | `2d2f510447cd50b7ba74eb03fde48899fa2578aad69b167775368652d061dd66` |
| [`morphogenesis/experiments/L1_field/x173_g11_s1014.compact.json`](../morphogenesis/experiments/L1_field/x173_g11_s1014.compact.json) | other | 185037 | `c4f835f4cbaf6dc90f45c3b925d28a72b7257448b8bd4ca12b27d9a260bc5b90` |
| [`morphogenesis/experiments/L1_field/x173_g11_s1015.compact.json`](../morphogenesis/experiments/L1_field/x173_g11_s1015.compact.json) | other | 194793 | `c6dd9f2b2d2f713bdc191fa53fc986eb868d15e9144edfca4e8b6ccd7739b7df` |
| [`morphogenesis/experiments/L1_field/x173_g11_s1016.compact.json`](../morphogenesis/experiments/L1_field/x173_g11_s1016.compact.json) | other | 164235 | `151b0cb1593d3413381bac501606d9ccfa6d8f8719b44a29a0d986a7ff3b4693` |
| [`morphogenesis/experiments/L1_field/x173_g11_s1017.compact.json`](../morphogenesis/experiments/L1_field/x173_g11_s1017.compact.json) | other | 207085 | `c60ccf70b7e249fc9798aece113f4d3f76a5bcaddf0155e94e2b2b4cb2b6f1c3` |
| [`morphogenesis/experiments/L1_field/x173_g11_s1018.compact.json`](../morphogenesis/experiments/L1_field/x173_g11_s1018.compact.json) | other | 199091 | `02131ae9a6a09024b67195f2d6b5f69b51937847a8e94f9111a2fb92ad6d8395` |
| [`morphogenesis/experiments/L1_field/x173_g11_s1019.compact.json`](../morphogenesis/experiments/L1_field/x173_g11_s1019.compact.json) | other | 195048 | `7004bd37aece4b30d161320e27d58095e281bd821109e166b4ef154363a284c2` |
| [`morphogenesis/experiments/L1_field/x173_g11_s1020.compact.json`](../morphogenesis/experiments/L1_field/x173_g11_s1020.compact.json) | other | 202699 | `b335850c264a376ca8da2d76a82b858d591742b5c12630d8dc98650df67bfb3e` |
| [`morphogenesis/experiments/L1_field/x173_g8_s1011.compact.json`](../morphogenesis/experiments/L1_field/x173_g8_s1011.compact.json) | other | 190756 | `452b8b7241b2c2c9e62ce1313d84a558d7801d41ec83a6fcb02c338a9beb52ab` |
| [`morphogenesis/experiments/L1_field/x173_g8_s1012.compact.json`](../morphogenesis/experiments/L1_field/x173_g8_s1012.compact.json) | other | 205664 | `53e528e4c5416ba1b0e75979bba6afe6b020077c6ea1721799c2986b829979ae` |
| [`morphogenesis/experiments/L1_field/x173_g8_s1013.compact.json`](../morphogenesis/experiments/L1_field/x173_g8_s1013.compact.json) | other | 189194 | `b846a051ee2e91a290802ae71451fa19a12f0164c4a9f878302485829c2e54c0` |
| [`morphogenesis/experiments/L1_field/x173_g8_s1014.compact.json`](../morphogenesis/experiments/L1_field/x173_g8_s1014.compact.json) | other | 193598 | `e34af9ea53c0c369374cf3625f810c794d23784baba3e54a6304c92207c7733b` |
| [`morphogenesis/experiments/L1_field/x173_g8_s1015.compact.json`](../morphogenesis/experiments/L1_field/x173_g8_s1015.compact.json) | other | 195641 | `46f9274c0bc89932aace4c9cc407739d7c7b875592a7890ff94b95dc6d05139a` |
| [`morphogenesis/experiments/L1_field/x173_g8_s1016.compact.json`](../morphogenesis/experiments/L1_field/x173_g8_s1016.compact.json) | other | 186170 | `0c08a1dd319a7a3ecfa2e02dd91e46b267039e91199a56b765647b06c3a21b0f` |
| [`morphogenesis/experiments/L1_field/x173_g8_s1017.compact.json`](../morphogenesis/experiments/L1_field/x173_g8_s1017.compact.json) | other | 185218 | `2b3f49a32a367ee724f7207eafb0fd522a25d36f622d36fe35de296e0e2a6ae7` |
| [`morphogenesis/experiments/L1_field/x173_g8_s1018.compact.json`](../morphogenesis/experiments/L1_field/x173_g8_s1018.compact.json) | other | 191356 | `2255336c8ae61a8d3dcd1bc6d065704919b8a61ca27b4a63aa838d5f54f333c0` |
| [`morphogenesis/experiments/L1_field/x173_g8_s1019.compact.json`](../morphogenesis/experiments/L1_field/x173_g8_s1019.compact.json) | other | 195652 | `0a931b113e262fc97bd978b205c277fc0530333b71bf8a56818bcfb7164df66c` |
| [`morphogenesis/experiments/L1_field/x173_g8_s1020.compact.json`](../morphogenesis/experiments/L1_field/x173_g8_s1020.compact.json) | other | 171760 | `275d61543f8422c4f3c48cd010090a18888274188963956e6d2e653b1a4d0e01` |
| [`morphogenesis/experiments/L1_field/x173_series_index.json`](../morphogenesis/experiments/L1_field/x173_series_index.json) | other | 2525 | `ca5538f07054419377e1573ac24b111c9b5462c3eafd8baf9dd20433cd68f3c8` |
| [`morphogenesis/experiments/L1_field/x17_homog_s171.json`](../morphogenesis/experiments/L1_field/x17_homog_s171.json) | other | 5807 | `52c8eb93322002fc2102b09e9c6b631fb9e063b2cc9ba880bf31ee910011cb07` |
| [`morphogenesis/experiments/L1_field/x17_homog_s172.json`](../morphogenesis/experiments/L1_field/x17_homog_s172.json) | other | 5679 | `ee73effb3e386db3c43c701b1ed18351cdb1a804b182f869daaa682e10dc09ac` |
| [`morphogenesis/experiments/L1_field/x17_homog_s173.json`](../morphogenesis/experiments/L1_field/x17_homog_s173.json) | other | 5550 | `4d27fae429cdf0dbd0ad9b89571e3319c0ab6070d1dcd31b473ea29c56f00465` |
| [`morphogenesis/experiments/L1_field/x17_homog_s174.json`](../morphogenesis/experiments/L1_field/x17_homog_s174.json) | other | 5856 | `ee24e46530b7f90e88f726f2401c999e4aa205c3fbf58f8c369ad4ccee4c80a5` |
| [`morphogenesis/experiments/L1_field/x17_homog_s175.json`](../morphogenesis/experiments/L1_field/x17_homog_s175.json) | other | 5525 | `a7bbf7f45b986081b2193da92f5656e57d9f28d8a5796a737b9ef318910f5df9` |
| [`morphogenesis/experiments/L1_field/x17_homog_s176.json`](../morphogenesis/experiments/L1_field/x17_homog_s176.json) | other | 5740 | `c0d23340c4a91417ff72706588422d88d58f446c4276c7dadb0d6e5ef43aaadc` |
| [`morphogenesis/experiments/L1_field/x17_homog_s177.json`](../morphogenesis/experiments/L1_field/x17_homog_s177.json) | other | 5772 | `2619a9c8f523840ade20acb8695c910657ca7952eae6e8dbfefa1fce75b5bbd2` |
| [`morphogenesis/experiments/L1_field/x17_homog_s178.json`](../morphogenesis/experiments/L1_field/x17_homog_s178.json) | other | 5790 | `4b505661b6c7d53f862ea5b1d1e96b5264c2255b36d1109cdc608f27b0cad32d` |
| [`morphogenesis/experiments/L1_field/x17_homog_s179.json`](../morphogenesis/experiments/L1_field/x17_homog_s179.json) | other | 5664 | `4a2c9750ed91708c9ea183293f0ff87a4e2c5dcb9c1bad60fb87887a664f08d5` |
| [`morphogenesis/experiments/L1_field/x17_homog_s180.json`](../morphogenesis/experiments/L1_field/x17_homog_s180.json) | other | 5605 | `48c5921826d9332bd285fd015cb4b10690a7730497a03830bbae38ffc4eaf5c2` |
| [`morphogenesis/experiments/L1_field/x17_static_s171.json`](../morphogenesis/experiments/L1_field/x17_static_s171.json) | other | 6359 | `ab29e7a9f3df4d8b6f826e514369ecda755c71881f9b5a05b76f7ef199a86c20` |
| [`morphogenesis/experiments/L1_field/x17_static_s172.json`](../morphogenesis/experiments/L1_field/x17_static_s172.json) | other | 6908 | `2fe2c3a981a7bb0270e7d31ec90b581ccc64994869c2963dc10c50957b9fc30f` |
| [`morphogenesis/experiments/L1_field/x17_static_s173.json`](../morphogenesis/experiments/L1_field/x17_static_s173.json) | other | 5995 | `60e22f78d8e4e5407a8074a401f905a77b8607e8e04071e17b0ad73aff34b0d5` |
| [`morphogenesis/experiments/L1_field/x17_static_s174.json`](../morphogenesis/experiments/L1_field/x17_static_s174.json) | other | 7370 | `fb8db68a01a182c11f9c96bc5828313b7555f95969e691088409841901b9c06e` |
| [`morphogenesis/experiments/L1_field/x17_static_s175.json`](../morphogenesis/experiments/L1_field/x17_static_s175.json) | other | 5894 | `729a40d7b771d689741165c9dc57074899e0094cf0dae3bee39cbf846c24f627` |
| [`morphogenesis/experiments/L1_field/x17_static_s176.json`](../morphogenesis/experiments/L1_field/x17_static_s176.json) | other | 6797 | `4043da569344a65b652145cd5c487ae1bdd1862e13a623f06fa0ecfef4474b59` |
| [`morphogenesis/experiments/L1_field/x17_static_s177.json`](../morphogenesis/experiments/L1_field/x17_static_s177.json) | other | 6088 | `67286bd87897db16d731afa944438af3aeb6223e8f28969ce0282df668e5fc19` |
| [`morphogenesis/experiments/L1_field/x17_static_s178.json`](../morphogenesis/experiments/L1_field/x17_static_s178.json) | other | 6300 | `e66f4711784ec98049e2b127a55be458548dd659dad8b78184edc265a0a55732` |
| [`morphogenesis/experiments/L1_field/x17_static_s179.json`](../morphogenesis/experiments/L1_field/x17_static_s179.json) | other | 5815 | `913c28ff35ec95e5493921b8a364ff303437e2e625a6a4b8c06c92ec1b85c2bb` |
| [`morphogenesis/experiments/L1_field/x17_static_s180.json`](../morphogenesis/experiments/L1_field/x17_static_s180.json) | other | 6838 | `146739e24c175eaf77e80f8d434480827a34d09d7d0b3b665c74c1c05e6b519f` |
| [`morphogenesis/experiments/L1_field/x18_globalnoise_s171.json`](../morphogenesis/experiments/L1_field/x18_globalnoise_s171.json) | other | 4978 | `4a509ac33ab6921366c0d597a514bffe8d37ad45e0dc7fec0a0308e464a03708` |
| [`morphogenesis/experiments/L1_field/x18_globalnoise_s172.json`](../morphogenesis/experiments/L1_field/x18_globalnoise_s172.json) | other | 4459 | `ec93f9df4241e63b4fc38f7e8caab34d12f636657f6ec38a100259beaea9d845` |
| [`morphogenesis/experiments/L1_field/x18_globalnoise_s173.json`](../morphogenesis/experiments/L1_field/x18_globalnoise_s173.json) | other | 4610 | `81e0a837e0a98390f065ffd7cea1229fb25f0a19b06e8afc10525fec6d6bec25` |
| [`morphogenesis/experiments/L1_field/x18_globalnoise_s174.json`](../morphogenesis/experiments/L1_field/x18_globalnoise_s174.json) | other | 4397 | `a46e3eabd39ade58898ba0581b2f1dd2152b212e4d831baea3fd082999454ce6` |
| [`morphogenesis/experiments/L1_field/x18_globalnoise_s175.json`](../morphogenesis/experiments/L1_field/x18_globalnoise_s175.json) | other | 4688 | `a4a455f46dc997f41ebff7e9871e0af4c8117d927221d55edb63578149b449dd` |
| [`morphogenesis/experiments/L1_field/x18_globalnoise_s176.json`](../morphogenesis/experiments/L1_field/x18_globalnoise_s176.json) | other | 4237 | `284b6a3586c834ea0ff0a4d566b9eb0c15b1f3938443380104b0ff9367de6f99` |
| [`morphogenesis/experiments/L1_field/x18_globalnoise_s177.json`](../morphogenesis/experiments/L1_field/x18_globalnoise_s177.json) | other | 4240 | `442c357820f8e9d4af582ab8915b3a5ac13e1358248f1898999e972e09113b23` |
| [`morphogenesis/experiments/L1_field/x18_globalnoise_s178.json`](../morphogenesis/experiments/L1_field/x18_globalnoise_s178.json) | other | 4438 | `f3790cf233b41bbe91d635a4701c7dff110892c93cb1dc6b810bf8206a78765b` |
| [`morphogenesis/experiments/L1_field/x18_globalnoise_s179.json`](../morphogenesis/experiments/L1_field/x18_globalnoise_s179.json) | other | 4404 | `5ebf56bda7163d0aaf55e72b8942add436d6be1ebf82997d80e5f8b56a41168a` |
| [`morphogenesis/experiments/L1_field/x18_globalnoise_s180.json`](../morphogenesis/experiments/L1_field/x18_globalnoise_s180.json) | other | 4314 | `2b184ff53e333d78467ec91bdeb0df4b8816d8e5c8cc8a3be10f6beedbd997b2` |
| [`morphogenesis/experiments/L1_field/x18_homog_s171.json`](../morphogenesis/experiments/L1_field/x18_homog_s171.json) | other | 4355 | `caf3247b12f9444d519914d7d2547301fd781b7ff084bed207ebacf16ae4d3de` |
| [`morphogenesis/experiments/L1_field/x18_homog_s172.json`](../morphogenesis/experiments/L1_field/x18_homog_s172.json) | other | 4375 | `0031bd081e8ead14d222966a62ca583cb556cfe2eea04df37d99a6cae530b3b9` |
| [`morphogenesis/experiments/L1_field/x18_homog_s173.json`](../morphogenesis/experiments/L1_field/x18_homog_s173.json) | other | 4277 | `1603dfedcdd67b2c9f9c77b6735d72189664e7c45b8fc4f9232c0184d4699109` |
| [`morphogenesis/experiments/L1_field/x18_homog_s174.json`](../morphogenesis/experiments/L1_field/x18_homog_s174.json) | other | 4466 | `400697ea61dd369c087cce9c5ceacca37150985cf677dea89284df89a3787ab1` |
| [`morphogenesis/experiments/L1_field/x18_homog_s175.json`](../morphogenesis/experiments/L1_field/x18_homog_s175.json) | other | 4281 | `7714e812cd57e669e512d70507c95d7689a3109af657eb4dad8d00be7d3b829c` |
| [`morphogenesis/experiments/L1_field/x18_homog_s176.json`](../morphogenesis/experiments/L1_field/x18_homog_s176.json) | other | 4436 | `c5d70fe79361e50c4c5055580cbaac623084edda1c009ea70ec539f7793813b9` |
| [`morphogenesis/experiments/L1_field/x18_homog_s177.json`](../morphogenesis/experiments/L1_field/x18_homog_s177.json) | other | 4305 | `2d6b8879b0113f6e73989c0e5d23c7fbbd07600d744ebd4b74599a30374a1775` |
| [`morphogenesis/experiments/L1_field/x18_homog_s178.json`](../morphogenesis/experiments/L1_field/x18_homog_s178.json) | other | 4553 | `5800fd12991c69a755a82d45ac1a1905e5e4771329b6b1f3a08d563dbc5ea354` |
| [`morphogenesis/experiments/L1_field/x18_homog_s179.json`](../morphogenesis/experiments/L1_field/x18_homog_s179.json) | other | 4354 | `529687ec64a85035063e27b2c0696e162c1c4b8d819a7a42575199617d60b721` |
| [`morphogenesis/experiments/L1_field/x18_homog_s180.json`](../morphogenesis/experiments/L1_field/x18_homog_s180.json) | other | 4301 | `c3867d0a43c374559331b245c231498ee19e91af5233f3a3585bda8223bed6d4` |
| [`morphogenesis/experiments/L1_field/x18_pattern_s171.json`](../morphogenesis/experiments/L1_field/x18_pattern_s171.json) | other | 4915 | `cf6414ded0cc22ede98a979d8662d651f8cac6db62b5eb6a778e07bdd580a95e` |
| [`morphogenesis/experiments/L1_field/x18_pattern_s172.json`](../morphogenesis/experiments/L1_field/x18_pattern_s172.json) | other | 5539 | `392447e89ac478a309f7b966db9c754d037d502da3665cc83731362e87920c67` |
| [`morphogenesis/experiments/L1_field/x18_pattern_s173.json`](../morphogenesis/experiments/L1_field/x18_pattern_s173.json) | other | 4619 | `bc8c521b94ccf98c3c04c08ab40e06b656b4fe75dcbf5f9091137545e6914d9d` |
| [`morphogenesis/experiments/L1_field/x18_pattern_s174.json`](../morphogenesis/experiments/L1_field/x18_pattern_s174.json) | other | 4561 | `de284139e520091158c7ff92a5b157bdb22fc1192541d9ee7e73a5f98346387a` |
| [`morphogenesis/experiments/L1_field/x18_pattern_s175.json`](../morphogenesis/experiments/L1_field/x18_pattern_s175.json) | other | 4523 | `878ca3764cbca53ac9344e72b067bb921b2be2f4803ee5f0ad256bbe6d28540f` |
| [`morphogenesis/experiments/L1_field/x18_pattern_s176.json`](../morphogenesis/experiments/L1_field/x18_pattern_s176.json) | other | 5173 | `ee2fbd27d57e70b69ae355bf521ef0077da5975e21eec4a3be422052e5f72569` |
| [`morphogenesis/experiments/L1_field/x18_pattern_s177.json`](../morphogenesis/experiments/L1_field/x18_pattern_s177.json) | other | 4634 | `03b576645cfcf35ea42bd0ef9dc74716d1464352b290f2b0bac9fb55f2d021b0` |
| [`morphogenesis/experiments/L1_field/x18_pattern_s178.json`](../morphogenesis/experiments/L1_field/x18_pattern_s178.json) | other | 5002 | `57ee0944bbf948e76ea881502e435b29af2a0e222f44d700512ca895a45d5a9a` |
| [`morphogenesis/experiments/L1_field/x18_pattern_s179.json`](../morphogenesis/experiments/L1_field/x18_pattern_s179.json) | other | 4544 | `2d808c48a1d11cc1296a4fb40fcf10b068502eb5e67e03008602335dc2dd1976` |
| [`morphogenesis/experiments/L1_field/x18_pattern_s180.json`](../morphogenesis/experiments/L1_field/x18_pattern_s180.json) | other | 4778 | `edb2d1a5c6a08f9b20af36fc24a9c50aa1d80c70fbc0447b647647dc6f9ed62a` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s181.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s181.json) | other | 4405 | `7d896678aa4fd9a30394589cb133c0f29c9af03617427c9aee9e30cf5167fbd5` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s182.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s182.json) | other | 4389 | `3d13758645de248ec3176e4d7c568746fa0ea6bd3b2ac5bb836be14f615a1d33` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s183.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s183.json) | other | 4276 | `c2d09e12011405316dd25d6a3412c3cf7bde2f0e799f8f4191f810567cb32988` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s184.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s184.json) | other | 4576 | `a2cb37723493daf67fa2c2e23463d133e31d5a1bd20846dffe2b36ab1904c319` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s185.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s185.json) | other | 4673 | `1c7720145a1aea67acc5d594da3b68eeff24dafee379d431d5ec491d1881a938` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s186.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s186.json) | other | 4509 | `04001bca92023dad75f728d627f901d29144bb180d8e2fcecedbd5d272719e0b` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s187.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s187.json) | other | 4361 | `b5dbb4647d3266b2e0f981c3f09049516beaaea3a9dcdc9059cf4fbc3757d3a7` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s188.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s188.json) | other | 4339 | `983f80114449fe46ca1d68a82084fdc3f42edd10332706100ae471a518027a97` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s189.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s189.json) | other | 4355 | `8e2acc84d9720b4f0dc455c181d1c0cefb9952f590c975e69cbbebcc85216f36` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s190.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s190.json) | other | 4375 | `70a2d16c66cd542dc4d183fe6044fce2543790b3098a7f92b02f7498278087c5` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s191.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s191.json) | other | 4519 | `9e65a8534de36e6d1fb63594be417751f345539e62d649db4c2d3b1e5596dd08` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s192.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s192.json) | other | 5019 | `e624591f869e4158c662cde2db6825ae236ed5628da9b691a7e812fee8d27d5b` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s193.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s193.json) | other | 4593 | `4a53536c7e0cea9d2292365df0e6502e7cc118e0eba56711e21eff8db1cb4b64` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s194.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s194.json) | other | 4383 | `8666a8fc0f6c3a295078c5752f3c632fb9b4024a10aff8172d146282ee23e131` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s195.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s195.json) | other | 4591 | `9e9a5d0fa14029b9eeeb42c1f7c168ef17ff2937cea96dc5c18b0b32f2e4995a` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s196.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s196.json) | other | 4431 | `f8d8c50870fc9d896e0f90a91d0dd5a24d4a198021a45b6ff1cff962b757d712` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s197.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s197.json) | other | 4695 | `7da57b8ef408d7c5d3103be4ca7766a10d46acc6cbfafdf0bae11defa0138fe9` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s198.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s198.json) | other | 4917 | `be695be29e838779d6392dad1a1a17542ad0cfbd84964117f0d8b29da2a1be10` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s199.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s199.json) | other | 4434 | `9b61a0b920f35227e9c341b73f0f23113b28e46db79b89cdc61cd41f5bd4e826` |
| [`morphogenesis/experiments/L1_field/x21_globalnoise_s200.json`](../morphogenesis/experiments/L1_field/x21_globalnoise_s200.json) | other | 4392 | `3decc0d433a3343e9c41e6dd6b4f7ed99a4cb214778609dfcdd5e704567761b1` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s181.json`](../morphogenesis/experiments/L1_field/x21_pattern_s181.json) | other | 4604 | `8d729cabb17e6d4214eed94c310b60d07982a5b7a471194263ef71d2a3ecd6da` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s182.json`](../morphogenesis/experiments/L1_field/x21_pattern_s182.json) | other | 4454 | `ad5e4c707bbc08d3ba0b675455c71313951c9ee21f16f692ba2052759a233ba1` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s183.json`](../morphogenesis/experiments/L1_field/x21_pattern_s183.json) | other | 4492 | `29d9d1aa34dcfc294d1e52490bd17c246f5cce793908d1c3194e8e573e36ca4d` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s184.json`](../morphogenesis/experiments/L1_field/x21_pattern_s184.json) | other | 4739 | `04f9aae514e506d542b183a30e3641f45f1680cf4f10b678a0ca0d1419f6f147` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s185.json`](../morphogenesis/experiments/L1_field/x21_pattern_s185.json) | other | 5908 | `5241c2a66839c34ed386e60a6a7b9d564538094d558c265f4489b8f562ba8258` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s186.json`](../morphogenesis/experiments/L1_field/x21_pattern_s186.json) | other | 4944 | `62c8c615ff88e72b7da4185574aec539851447f0123f1b3c3ba0181ef6f9cbfe` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s187.json`](../morphogenesis/experiments/L1_field/x21_pattern_s187.json) | other | 4838 | `e1302f64285ec35092eae1b6bfade7eb23bbd2a0ea2aeebf1916491b16afdec0` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s188.json`](../morphogenesis/experiments/L1_field/x21_pattern_s188.json) | other | 4636 | `1af40e4a563b27fc5118d19194dcc1aed0a7d35a6076be1df17afc85212e9142` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s189.json`](../morphogenesis/experiments/L1_field/x21_pattern_s189.json) | other | 4485 | `2d1600ad0f80b9bc5d62a96eaa32e21a6fbb271df1a4b2cf5456294e051c671f` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s190.json`](../morphogenesis/experiments/L1_field/x21_pattern_s190.json) | other | 5153 | `06626b6f9c4b4b417131a591b9d118f5e38012fc2c6f1c2d12d137d2097fb421` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s191.json`](../morphogenesis/experiments/L1_field/x21_pattern_s191.json) | other | 4883 | `0c2928ebb7680638286dfb40c71266271abcd70db3ae62ff900101cc25a37990` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s192.json`](../morphogenesis/experiments/L1_field/x21_pattern_s192.json) | other | 4974 | `3faeff9a08c0b7582f84d37ddab8161b2d9c275c5d1d04ba1cde4b775249d279` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s193.json`](../morphogenesis/experiments/L1_field/x21_pattern_s193.json) | other | 4623 | `8e9d11ada4e69d82db7eae77a3f76714fc3eaa418da5b1d86d2b09843d716f1a` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s194.json`](../morphogenesis/experiments/L1_field/x21_pattern_s194.json) | other | 4370 | `a46345bd9b269b233e7e34c028f92a34750ec91b7e64dd256159b33276363121` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s195.json`](../morphogenesis/experiments/L1_field/x21_pattern_s195.json) | other | 4587 | `1c783e4fad619716fb34b7901fd6c1171a2b31e6dcc8dc246d2d64a5cc17f7ce` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s196.json`](../morphogenesis/experiments/L1_field/x21_pattern_s196.json) | other | 4501 | `f8aa6a460bb81a231b59e5938706205d92f2af51e0614961fad9b65a9bbd085b` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s197.json`](../morphogenesis/experiments/L1_field/x21_pattern_s197.json) | other | 4696 | `5b53d06ecc543e1d6195da2cf9b3257e0fb22d163d748c3e76494eee7f101247` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s198.json`](../morphogenesis/experiments/L1_field/x21_pattern_s198.json) | other | 4743 | `5eebd6af48b92f799224a7d6babfaa3f88d588628fc1e40914d9a0fa3eab6d6a` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s199.json`](../morphogenesis/experiments/L1_field/x21_pattern_s199.json) | other | 4485 | `1b4b789b7774b3c532880dd9df3d19eee31204d10c9e0a197acd412ea81668a2` |
| [`morphogenesis/experiments/L1_field/x21_pattern_s200.json`](../morphogenesis/experiments/L1_field/x21_pattern_s200.json) | other | 4536 | `dfa04b94aacbe6e5170edbfdaac6f24cf42a1c217c2d0fd6ee2df80b68d82390` |
| [`morphogenesis/experiments/L1_field/x23_homog_s171.json`](../morphogenesis/experiments/L1_field/x23_homog_s171.json) | other | 6020 | `8095e0e63fc4bc412a2a9f4fba4b3a8ebc626f174630e3aa73431a9d8f119991` |
| [`morphogenesis/experiments/L1_field/x23_homog_s172.json`](../morphogenesis/experiments/L1_field/x23_homog_s172.json) | other | 6082 | `0423b0f747b1569b269bafa4b911bdce5ae87a1faba8b8984d4ac1bf9729489a` |
| [`morphogenesis/experiments/L1_field/x23_homog_s173.json`](../morphogenesis/experiments/L1_field/x23_homog_s173.json) | other | 5866 | `13b4d4232f550b2accef60daa03ba73d0286b54fe581c7a020e077ec279cdefa` |
| [`morphogenesis/experiments/L1_field/x23_homog_s174.json`](../morphogenesis/experiments/L1_field/x23_homog_s174.json) | other | 6166 | `760866d1e5d92c743ceba4ed8dec7a85ed9c9ae52b34db8772514d25f48bc684` |
| [`morphogenesis/experiments/L1_field/x23_homog_s175.json`](../morphogenesis/experiments/L1_field/x23_homog_s175.json) | other | 5868 | `e28ec9998b1b49f7b0a00235c7959edd9e0f537dabd8376f5cf3c9e4a28c72d2` |
| [`morphogenesis/experiments/L1_field/x23_homog_s176.json`](../morphogenesis/experiments/L1_field/x23_homog_s176.json) | other | 6226 | `08fb25bfd7c018ee798cca70bf31e3d6eec3eb5f8053f2a151c7bd3069c81b72` |
| [`morphogenesis/experiments/L1_field/x23_homog_s177.json`](../morphogenesis/experiments/L1_field/x23_homog_s177.json) | other | 5950 | `de9e2dc047868dca93a4a74e41879f5ca91cf7f56492ee8f7b49e3ad9164c3d7` |
| [`morphogenesis/experiments/L1_field/x23_homog_s178.json`](../morphogenesis/experiments/L1_field/x23_homog_s178.json) | other | 6236 | `4de0dffa8279a468ab9c877be0d0d9a39e15bcd7955f067d774188e6eb92b02b` |
| [`morphogenesis/experiments/L1_field/x23_homog_s179.json`](../morphogenesis/experiments/L1_field/x23_homog_s179.json) | other | 5987 | `b1edc570c5a86dfcfc5d695992a8a3a9a1f3037bb85ea2f2cfa1d035e8b13385` |
| [`morphogenesis/experiments/L1_field/x23_homog_s180.json`](../morphogenesis/experiments/L1_field/x23_homog_s180.json) | other | 5856 | `c35cf404fba1dd34f7d53d23fecfc58355a2cf3af5121969c4cedda22ccf5201` |
| [`morphogenesis/experiments/L1_field/x23_static_s171.json`](../morphogenesis/experiments/L1_field/x23_static_s171.json) | other | 6929 | `c2a67321640cd32574f75970ae6d9f16c7ab4630c7d950eb5861d05e38daedc3` |
| [`morphogenesis/experiments/L1_field/x23_static_s172.json`](../morphogenesis/experiments/L1_field/x23_static_s172.json) | other | 7853 | `3c0170be6ab5842a2333a11f5e51d63abd8f92417cc1390150c948efa17582ea` |
| [`morphogenesis/experiments/L1_field/x23_static_s173.json`](../morphogenesis/experiments/L1_field/x23_static_s173.json) | other | 6406 | `b4444aec7c749717b5daad687106c7cd4df55924b4c81aaa7934492d5f4c2f01` |
| [`morphogenesis/experiments/L1_field/x23_static_s174.json`](../morphogenesis/experiments/L1_field/x23_static_s174.json) | other | 6835 | `1c483de6e7b4235684a3ca462b667b5547e913dd0a3247b501c16400d5224a98` |
| [`morphogenesis/experiments/L1_field/x23_static_s175.json`](../morphogenesis/experiments/L1_field/x23_static_s175.json) | other | 6448 | `7d2f762b2a40629a2fbf49d259157f883c9e1e79f3a56b2a2bb0b6a984450c78` |
| [`morphogenesis/experiments/L1_field/x23_static_s176.json`](../morphogenesis/experiments/L1_field/x23_static_s176.json) | other | 7246 | `67ccfcf1f41f784f145b029003adadd7881aadd76862ce887d7b8f180eef1e24` |
| [`morphogenesis/experiments/L1_field/x23_static_s177.json`](../morphogenesis/experiments/L1_field/x23_static_s177.json) | other | 6365 | `a6d1b1fdb9ad1998d839630c77df3c39e693b1e7de3b4f6f8e7756b2b00bb7f5` |
| [`morphogenesis/experiments/L1_field/x23_static_s178.json`](../morphogenesis/experiments/L1_field/x23_static_s178.json) | other | 6869 | `274488a0fff4a33f94050db0a4c25cf614e3e8cdd07c9494f70e34985c344d72` |
| [`morphogenesis/experiments/L1_field/x23_static_s179.json`](../morphogenesis/experiments/L1_field/x23_static_s179.json) | other | 6217 | `e21574be5082187eb40795b1182f49ea74cf2d3d75976a775fc1002c80d6d1ec` |
| [`morphogenesis/experiments/L1_field/x23_static_s180.json`](../morphogenesis/experiments/L1_field/x23_static_s180.json) | other | 6807 | `8c3835b3c37e25784371b0ec6704b5ddb456c7f72e9c1b4e933579c5055189f2` |
| [`morphogenesis/experiments/L1_field/x23_static_s181.json`](../morphogenesis/experiments/L1_field/x23_static_s181.json) | other | 6511 | `744c1c68031e3d9dfd61bc99c797532d1bb5c7cfea6738374d0d40b119d9a3ba` |
| [`morphogenesis/experiments/L1_field/x23_static_s182.json`](../morphogenesis/experiments/L1_field/x23_static_s182.json) | other | 6568 | `e98bd1d6bd09744c862b9b4f8832fc7eef12a3b833f5cbfdd9656a3d3598726e` |
| [`morphogenesis/experiments/L1_field/x23_static_s183.json`](../morphogenesis/experiments/L1_field/x23_static_s183.json) | other | 6536 | `3798b818b5e8d791c34c6929e3c269509d89cb81b5edbf99507e52f4dfbc40d1` |
| [`morphogenesis/experiments/L1_field/x23_static_s184.json`](../morphogenesis/experiments/L1_field/x23_static_s184.json) | other | 7255 | `9c25b2eb44a5d658a4adb582ef572637bfc16cfbf010fd343035542a37d85157` |
| [`morphogenesis/experiments/L1_field/x37_null_s171.json`](../morphogenesis/experiments/L1_field/x37_null_s171.json) | other | 38747 | `845f424ddc00c21f41032fea13f2574e16331c6cf1fad99335bd8027d75a47f1` |
| [`morphogenesis/experiments/L1_field/x37_null_s172.json`](../morphogenesis/experiments/L1_field/x37_null_s172.json) | other | 38755 | `9089ac89e53e5f236776423f6d3cdcaa1f4edb62a6079c291b0a31b5a3c57c5e` |
| [`morphogenesis/experiments/L1_field/x37_null_s173.json`](../morphogenesis/experiments/L1_field/x37_null_s173.json) | other | 38750 | `47b87c08bcdb8d070ec6e0545b710cb1d5c592cf164331dc0cf3728b0f4deaf8` |
| [`morphogenesis/experiments/L1_field/x37_null_s174.json`](../morphogenesis/experiments/L1_field/x37_null_s174.json) | other | 38759 | `8e6692429616d8690a888e06fd3922035bb10b476fa201a1ab1aed5d4a8fdb58` |
| [`morphogenesis/experiments/L1_field/x37_null_s175.json`](../morphogenesis/experiments/L1_field/x37_null_s175.json) | other | 38748 | `197ebbca4fe32df6ffddcc52c1d2037c5cad4b6d0a3dd14107d380803240d902` |
| [`morphogenesis/experiments/L1_field/x37_null_s176.json`](../morphogenesis/experiments/L1_field/x37_null_s176.json) | other | 38747 | `f0ea55ed62acc0937c3129ef40605073e526575398f48e80dc4929c12a4f3779` |
| [`morphogenesis/experiments/L1_field/x37_null_s177.json`](../morphogenesis/experiments/L1_field/x37_null_s177.json) | other | 38752 | `d9ae433f72c58308f18bfe280ab061dd4c0b3b6bc2f65173d29c225be00fca9f` |
| [`morphogenesis/experiments/L1_field/x37_null_s178.json`](../morphogenesis/experiments/L1_field/x37_null_s178.json) | other | 38755 | `3dec9eba79442e09ea07973675dcab2899e5a7202d49b3c245a55760d0919ee3` |
| [`morphogenesis/experiments/L1_field/x37_null_s179.json`](../morphogenesis/experiments/L1_field/x37_null_s179.json) | other | 38762 | `a46de3f0a9c41bddd38b6c49a4b02f2364c75d2be215a0298073341607ca90f8` |
| [`morphogenesis/experiments/L1_field/x37_null_s180.json`](../morphogenesis/experiments/L1_field/x37_null_s180.json) | other | 38763 | `d681b4c9e567fd008115214332605da0ded60112fdda6e13240434a3678f8f5f` |
| [`morphogenesis/experiments/L1_field/x37_sel_s171.json`](../morphogenesis/experiments/L1_field/x37_sel_s171.json) | other | 15733 | `3522b8254b3a75abe82426753a8daab9e8ba1cb9a792510a46b47e0396bf6eef` |
| [`morphogenesis/experiments/L1_field/x37_sel_s172.json`](../morphogenesis/experiments/L1_field/x37_sel_s172.json) | other | 12307 | `0297d5e3b128a54f14bd309c78f69da972400488f62d513be341c8434b72ff9e` |
| [`morphogenesis/experiments/L1_field/x37_sel_s173.json`](../morphogenesis/experiments/L1_field/x37_sel_s173.json) | other | 10775 | `7bd3c49579c8cf5d9fa82e4de993d95776efbf59f37c8381b21501ae9b9eb16e` |
| [`morphogenesis/experiments/L1_field/x37_sel_s174.json`](../morphogenesis/experiments/L1_field/x37_sel_s174.json) | other | 12831 | `5c7419c9e589f90494930881afb1530878b70b690fbe91c044e12d87a9b71e85` |
| [`morphogenesis/experiments/L1_field/x37_sel_s175.json`](../morphogenesis/experiments/L1_field/x37_sel_s175.json) | other | 11855 | `8627ab7153b3168069f9adbddd032fbcdec76e982fcfe334c11595c48a62a62c` |
| [`morphogenesis/experiments/L1_field/x37_sel_s176.json`](../morphogenesis/experiments/L1_field/x37_sel_s176.json) | other | 12780 | `9784955a08bb8611bf2beaa82f3b91efa1e872a6b625c86429f89ce9a030f549` |
| [`morphogenesis/experiments/L1_field/x37_sel_s177.json`](../morphogenesis/experiments/L1_field/x37_sel_s177.json) | other | 11867 | `df45ab1144da353ca3537b593360ea4ba5de13e7a6150ba848a0894f42ea53d6` |
| [`morphogenesis/experiments/L1_field/x37_sel_s178.json`](../morphogenesis/experiments/L1_field/x37_sel_s178.json) | other | 12275 | `3081e492ba9468faa3c7afb95046ae2bd3d9227c92c1cd28f8853c0aa877f82d` |
| [`morphogenesis/experiments/L1_field/x37_sel_s179.json`](../morphogenesis/experiments/L1_field/x37_sel_s179.json) | other | 11381 | `bdb1fa3ceee6e2734062b062aa96720897c5433e2f99d6ab8e3fe83ae6ea89e9` |
| [`morphogenesis/experiments/L1_field/x37_sel_s180.json`](../morphogenesis/experiments/L1_field/x37_sel_s180.json) | other | 11574 | `7a4c186d9c2a8d150330db2a3c0066582cfe24ef8c56d2bf5b89e1519db6b334` |
| [`morphogenesis/experiments/L1_field/x48_mem0_s171.json`](../morphogenesis/experiments/L1_field/x48_mem0_s171.json) | other | 36225 | `b23e2647374f35be4e00e418cf845eb0c455e49211776469dd75cb31f7a62641` |
| [`morphogenesis/experiments/L1_field/x48_mem0_s172.json`](../morphogenesis/experiments/L1_field/x48_mem0_s172.json) | other | 35086 | `c6bc751b3754376087fe20e2753ee29e62ee9f470dbbc38fca9b72e2e3b3a193` |
| [`morphogenesis/experiments/L1_field/x48_mem0_s173.json`](../morphogenesis/experiments/L1_field/x48_mem0_s173.json) | other | 34698 | `3800173aa70e3560ffd6ed819a26662e0a783705f2d60fa55b4082b8818eadad` |
| [`morphogenesis/experiments/L1_field/x48_mem0_s174.json`](../morphogenesis/experiments/L1_field/x48_mem0_s174.json) | other | 33853 | `5afffb6b9d6ea029b56acab43b1f0f27666943b838c9ecb935aac6bdcc5de491` |
| [`morphogenesis/experiments/L1_field/x48_mem0_s175.json`](../morphogenesis/experiments/L1_field/x48_mem0_s175.json) | other | 33557 | `4e258639df511b6b1bd3a8618ea83335e604b49549f837bd9be623ab3b0097fe` |
| [`morphogenesis/experiments/L1_field/x48_mem0_s176.json`](../morphogenesis/experiments/L1_field/x48_mem0_s176.json) | other | 36539 | `546e2c754b99de1feeaf42a4de0c5a2aba5b02aeefc2376204b22f6286d23134` |
| [`morphogenesis/experiments/L1_field/x48_mem0_s177.json`](../morphogenesis/experiments/L1_field/x48_mem0_s177.json) | other | 34681 | `0860eaa839b361a887694db568b7ff8a03a09460c8402ad178079006c1f10189` |
| [`morphogenesis/experiments/L1_field/x48_mem0_s178.json`](../morphogenesis/experiments/L1_field/x48_mem0_s178.json) | other | 33809 | `b3e7a46ee399ace7d43b610f949fa27817b613b7cb6ddcb7da35fa1981b78ac7` |
| [`morphogenesis/experiments/L1_field/x48_mem0_s179.json`](../morphogenesis/experiments/L1_field/x48_mem0_s179.json) | other | 34816 | `94f8db208b1286ce75354d73e5aac923325bfb089cd610c2c1008e4b42e3395d` |
| [`morphogenesis/experiments/L1_field/x48_mem0_s180.json`](../morphogenesis/experiments/L1_field/x48_mem0_s180.json) | other | 34404 | `9e8687b3887138588a54f0eeedfc6e08c156af18863759f65bdc7fb4e0fc283e` |
| [`morphogenesis/experiments/L1_field/x48_mem100_s171.json`](../morphogenesis/experiments/L1_field/x48_mem100_s171.json) | other | 26210 | `c91409b766c45ab291df71c4530b9a6dcb6bcda4b96c0bfaa04b1e191d30b35e` |
| [`morphogenesis/experiments/L1_field/x48_mem100_s172.json`](../morphogenesis/experiments/L1_field/x48_mem100_s172.json) | other | 26372 | `66a192b3500dff24f81cab61012175ae1637a559684e39f2f502e962233fc66f` |
| [`morphogenesis/experiments/L1_field/x48_mem100_s173.json`](../morphogenesis/experiments/L1_field/x48_mem100_s173.json) | other | 26643 | `c53ee6b9856dadcf08fc6ab81b4f01b62c4c09e2780c70f105d0b232d2e63f92` |
| [`morphogenesis/experiments/L1_field/x48_mem100_s174.json`](../morphogenesis/experiments/L1_field/x48_mem100_s174.json) | other | 28546 | `c10de079a1ad761f1e7e661df035862168cbe726188411492092bebf65845108` |
| [`morphogenesis/experiments/L1_field/x48_mem100_s175.json`](../morphogenesis/experiments/L1_field/x48_mem100_s175.json) | other | 28362 | `281e373001814221632e8aff7f106d6022f8d744697341980faaefe1f039dd7d` |
| [`morphogenesis/experiments/L1_field/x48_mem100_s176.json`](../morphogenesis/experiments/L1_field/x48_mem100_s176.json) | other | 27205 | `9dfd1985c18d4f9b73900056d69ffee02025eabad8bf6fae8209657dc041f9e8` |
| [`morphogenesis/experiments/L1_field/x48_mem100_s177.json`](../morphogenesis/experiments/L1_field/x48_mem100_s177.json) | other | 27496 | `bd203ed13b3513d128695eefb21f216ecb1f142bd8c76bb5783f365f1883dab5` |
| [`morphogenesis/experiments/L1_field/x48_mem100_s178.json`](../morphogenesis/experiments/L1_field/x48_mem100_s178.json) | other | 29230 | `d32894ba6ec8ab437b6f1ed3ed7cabd828a459ab8012986c8e03de0012248114` |
| [`morphogenesis/experiments/L1_field/x48_mem100_s179.json`](../morphogenesis/experiments/L1_field/x48_mem100_s179.json) | other | 28788 | `6a5b73b24a323e524ae3ebf97fee639e235c60114c01dfff487b4d78f46d5b8d` |
| [`morphogenesis/experiments/L1_field/x48_mem100_s180.json`](../morphogenesis/experiments/L1_field/x48_mem100_s180.json) | other | 27234 | `34ed6aa5e60e2e8a0985eca0ac2496c57f3cc5a8d16fb7d610489fe379457257` |
| [`morphogenesis/experiments/L1_field/x48_mem30_s171.json`](../morphogenesis/experiments/L1_field/x48_mem30_s171.json) | other | 31011 | `e8dccbc1985de31438e6c14819a0bd9c6662837ecd439d75c770076ef9f8a388` |
| [`morphogenesis/experiments/L1_field/x48_mem30_s172.json`](../morphogenesis/experiments/L1_field/x48_mem30_s172.json) | other | 33146 | `cde08b62b34110f9faa331c1bd87ce65f60902e276b5ca746036a5f7233a5200` |
| [`morphogenesis/experiments/L1_field/x48_mem30_s173.json`](../morphogenesis/experiments/L1_field/x48_mem30_s173.json) | other | 31419 | `287d2d390820f35f2403be9620cf1718b760cfefa640b05e17ee769da60f2360` |
| [`morphogenesis/experiments/L1_field/x48_mem30_s174.json`](../morphogenesis/experiments/L1_field/x48_mem30_s174.json) | other | 30879 | `532ba2be856087fff68b5e429b3354c0d4600a29983b4af53bc4b713d97d3c82` |
| [`morphogenesis/experiments/L1_field/x48_mem30_s175.json`](../morphogenesis/experiments/L1_field/x48_mem30_s175.json) | other | 32148 | `37635eecba75d68750e46ec13e1f4bb480e4b579a0625dd5647e6c63b5511d0b` |
| [`morphogenesis/experiments/L1_field/x48_mem30_s176.json`](../morphogenesis/experiments/L1_field/x48_mem30_s176.json) | other | 32990 | `f41e73514fdce2feee8a0e7c2d2e85db6e26b8ceed24abbde6b705461ef9afbe` |
| [`morphogenesis/experiments/L1_field/x48_mem30_s177.json`](../morphogenesis/experiments/L1_field/x48_mem30_s177.json) | other | 31861 | `94bcb7106a35e4fca3786d660858a1f7dc3f52998e3179334f0612c7afafb820` |
| [`morphogenesis/experiments/L1_field/x48_mem30_s178.json`](../morphogenesis/experiments/L1_field/x48_mem30_s178.json) | other | 34271 | `c67081a925cd89e6ec82a25604dfda559cd8c3ac7669f0ff95a2b631a954c179` |
| [`morphogenesis/experiments/L1_field/x48_mem30_s179.json`](../morphogenesis/experiments/L1_field/x48_mem30_s179.json) | other | 35577 | `9c3cbfdf477edfdbe0996e4a0f8005bd09ffc05aa976596bcec98945159a15b6` |
| [`morphogenesis/experiments/L1_field/x48_mem30_s180.json`](../morphogenesis/experiments/L1_field/x48_mem30_s180.json) | other | 34262 | `f1fe27c2d2c3462ebe5a961e8c1786cffdf05069085f4627375f182330f368ae` |
| [`morphogenesis/experiments/L1_field/x49_none_s171.json`](../morphogenesis/experiments/L1_field/x49_none_s171.json) | other | 110379 | `3f4f7cecadd43c81de2c8351958fcc4af15ca099501fedeef51d1d6f5e19f9e1` |
| [`morphogenesis/experiments/L1_field/x49_none_s172.json`](../morphogenesis/experiments/L1_field/x49_none_s172.json) | other | 118330 | `d31f9b5682fea1935d8300551fca17bd38e9419fac026ca0e9a18ff79b2be1df` |
| [`morphogenesis/experiments/L1_field/x49_none_s173.json`](../morphogenesis/experiments/L1_field/x49_none_s173.json) | other | 101539 | `99c05c7a6f3a9831d542fa7489ded44a22211c4f548da99b6db7d1aee89a8634` |
| [`morphogenesis/experiments/L1_field/x49_none_s174.json`](../morphogenesis/experiments/L1_field/x49_none_s174.json) | other | 104662 | `fbb60a5833844903fe1764d4c5393dadf865cf63d843b398b529a2879d87944e` |
| [`morphogenesis/experiments/L1_field/x49_none_s175.json`](../morphogenesis/experiments/L1_field/x49_none_s175.json) | other | 110940 | `f816f0cf2fce3338a2d1d57629ba0f2ed98e313753c500681d9047f5aec04864` |
| [`morphogenesis/experiments/L1_field/x49_none_s176.json`](../morphogenesis/experiments/L1_field/x49_none_s176.json) | other | 109615 | `e87e1b2cfeba46f7268c43816e8c47dbaad75e45c012284c77a4d902ce470262` |
| [`morphogenesis/experiments/L1_field/x49_none_s177.json`](../morphogenesis/experiments/L1_field/x49_none_s177.json) | other | 120446 | `8bb51309430c176db9052c9a83a0a9cbcf7d7629618adda570a06cdf4634fd81` |
| [`morphogenesis/experiments/L1_field/x49_none_s178.json`](../morphogenesis/experiments/L1_field/x49_none_s178.json) | other | 105464 | `c08ef74af77a59ceabecd6c640ff8ec8929403778fb1c1b5e24a91eeea2bbe11` |
| [`morphogenesis/experiments/L1_field/x49_none_s179.json`](../morphogenesis/experiments/L1_field/x49_none_s179.json) | other | 119466 | `23e579a6c28c14659491fcbf74f54794e6c3a0627d253d9415502dbb45bd520b` |
| [`morphogenesis/experiments/L1_field/x49_none_s180.json`](../morphogenesis/experiments/L1_field/x49_none_s180.json) | other | 119410 | `f043a09f6b31d14b9c672fd489da28204852643d9b21179ba30637bef6ceb20e` |
| [`morphogenesis/experiments/L1_field/x49_omitted_s171.json`](../morphogenesis/experiments/L1_field/x49_omitted_s171.json) | other | 111639 | `4345df0595e9d9704cb6fc886e0fbd66b6d1bd3f8dd753d8116a3214bfa18b47` |
| [`morphogenesis/experiments/L1_field/x49_omitted_s172.json`](../morphogenesis/experiments/L1_field/x49_omitted_s172.json) | other | 109305 | `3f23d5a2f0451349d27a808d3506a42c2a9a326b5f9eb785c25e0949a71d1202` |
| [`morphogenesis/experiments/L1_field/x49_omitted_s173.json`](../morphogenesis/experiments/L1_field/x49_omitted_s173.json) | other | 107036 | `c25c9588120811e8ea71c495baa8f46ad3c4e3fee6bf7523b39e904da2d3efa7` |
| [`morphogenesis/experiments/L1_field/x49_omitted_s174.json`](../morphogenesis/experiments/L1_field/x49_omitted_s174.json) | other | 106950 | `abd853e2dc836bdb5bbec24f149f7f816690c93eedecdc2f496447e4a1442928` |
| [`morphogenesis/experiments/L1_field/x49_omitted_s175.json`](../morphogenesis/experiments/L1_field/x49_omitted_s175.json) | other | 112606 | `2fbd965aba73a24237a6395c6834fcb0e6c56e2c6c8d800b45d8d33ac56fe496` |
| [`morphogenesis/experiments/L1_field/x49_omitted_s176.json`](../morphogenesis/experiments/L1_field/x49_omitted_s176.json) | other | 107427 | `7397f4cdd6e469f8c0a85ab1d7f8ff4768846638011347695aa07de6c8cb3d83` |
| [`morphogenesis/experiments/L1_field/x49_omitted_s177.json`](../morphogenesis/experiments/L1_field/x49_omitted_s177.json) | other | 110128 | `f932dbcf1be81588e63c9ba9ee427bca90e53e81bfb757129d80aa149ddf5b43` |
| [`morphogenesis/experiments/L1_field/x49_omitted_s178.json`](../morphogenesis/experiments/L1_field/x49_omitted_s178.json) | other | 115530 | `1c765f2cd6751fc54348b3fd29ca1a630915fccc3400eb1053b6b2b998700b2c` |
| [`morphogenesis/experiments/L1_field/x49_omitted_s179.json`](../morphogenesis/experiments/L1_field/x49_omitted_s179.json) | other | 110393 | `75f9de1e84d0cfecff5b9a5b0e9078298c6c07d5814757726c5a3fb09f64c810` |
| [`morphogenesis/experiments/L1_field/x49_omitted_s180.json`](../morphogenesis/experiments/L1_field/x49_omitted_s180.json) | other | 116098 | `24ab827107e3f17c3b76619b2923f4b4e30c58371328678b13bb028fe6533a00` |
| [`morphogenesis/experiments/L1_field/x49_periodic_s171.json`](../morphogenesis/experiments/L1_field/x49_periodic_s171.json) | other | 115094 | `377005450c07ae9b47bf9be621f0e62b8715c2b4882aaa2b759f48567bd1b9e7` |
| [`morphogenesis/experiments/L1_field/x49_periodic_s172.json`](../morphogenesis/experiments/L1_field/x49_periodic_s172.json) | other | 105467 | `b18cf81843dee480fc1b1a8c6cb25e4a570ea72473aa7b33edfcd98346a1cc90` |
| [`morphogenesis/experiments/L1_field/x49_periodic_s173.json`](../morphogenesis/experiments/L1_field/x49_periodic_s173.json) | other | 110158 | `222d88caa456314e2d1b486c5f737360ac55e776ebec07b732c663bc4c24b6c9` |
| [`morphogenesis/experiments/L1_field/x49_periodic_s174.json`](../morphogenesis/experiments/L1_field/x49_periodic_s174.json) | other | 106204 | `650fa6c210e53872a340e12e6e3c2743f8aabf39f1e701ddb640e2f9b61bcd51` |
| [`morphogenesis/experiments/L1_field/x49_periodic_s175.json`](../morphogenesis/experiments/L1_field/x49_periodic_s175.json) | other | 110068 | `574855b3460f0c447726a946b2ee95696a5800abaccb59a524b252cfead3a1c6` |
| [`morphogenesis/experiments/L1_field/x49_periodic_s176.json`](../morphogenesis/experiments/L1_field/x49_periodic_s176.json) | other | 109973 | `06a1389d9f07942bc3bdd46d27a0a0ad88b85208117c40fdc9f291b8fc27d84d` |
| [`morphogenesis/experiments/L1_field/x49_periodic_s177.json`](../morphogenesis/experiments/L1_field/x49_periodic_s177.json) | other | 109587 | `52140b207da1606319cfd436c48f33b5bdedca853f9d1f75a01e1d9a99904459` |
| [`morphogenesis/experiments/L1_field/x49_periodic_s178.json`](../morphogenesis/experiments/L1_field/x49_periodic_s178.json) | other | 117207 | `c043671d0e2402fcbef766302159814e00e70fa01d5993b784969208e8d1989a` |
| [`morphogenesis/experiments/L1_field/x49_periodic_s179.json`](../morphogenesis/experiments/L1_field/x49_periodic_s179.json) | other | 113938 | `645b80269b66ce08f4144867c950b7f8b4bbf2974b2d8501501f8487054293c3` |
| [`morphogenesis/experiments/L1_field/x49_periodic_s180.json`](../morphogenesis/experiments/L1_field/x49_periodic_s180.json) | other | 117521 | `78649c311434653a167390097c50689915c0a8aee8c242013bfe0c205054c3db` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_homog_s171.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_homog_s171.json) | other | 28796 | `592adb851930e58d1d5388dd3c2420393dbc512e432642980a1179644b40928d` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_homog_s172.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_homog_s172.json) | other | 27339 | `162dbe73a3b53133b39d36aef7f68ebadcb0ca2cc39ef22126a08f717ba1c8b5` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_homog_s173.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_homog_s173.json) | other | 21191 | `90011a2bbc917834c9e23b6aef2d20ea3af1e44e65cac0dc8bea5cca4aad5f0a` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_homog_s174.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_homog_s174.json) | other | 21624 | `e9af01f3cef4f11dde0e570195ea67c2531cd65d746bf67ea4fb66c769fa3772` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_homog_s175.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_homog_s175.json) | other | 35872 | `aa56457200e20d4f7e057055fa0cc1586a852f82f7554075e68816287f1e0566` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_homog_s176.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_homog_s176.json) | other | 33462 | `acba3af24471eaeb1e07d3bf92d60315efbdb06b16ca315eaec716770de25e73` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_homog_s177.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_homog_s177.json) | other | 21172 | `993a052c5e2603ecae1fc878f5785c57881ddda5a949d015b4ca490c1cd71ed5` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_homog_s178.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_homog_s178.json) | other | 30676 | `fa1630df6244bdfd58b8c0a4f430c5c5318d25f73371fb7b1aab7c1859a8d9af` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_homog_s179.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_homog_s179.json) | other | 20488 | `b5d26ef32c73f9c1e71994ff64f3097e11eeac5b2e9ab7b665c62c01d37dab30` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_homog_s180.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_homog_s180.json) | other | 18457 | `30ddf8e680f8af60967f5bdbfd9913c066ca13d299a952d7e346dd325f56fb04` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_static_s171.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_static_s171.json) | other | 22805 | `7b72aa1b43b796e26cb2961575f8a5134a57ab24590e89069a31460f1f363d90` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_static_s172.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_static_s172.json) | other | 24670 | `9ff1b1e54c74dbdbdba42d3c853eb169023e648996ca5a2b848dce6cdffe142b` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_static_s173.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_static_s173.json) | other | 26967 | `c9ad0226affdd7a63ee3065bc092366449aa0d47c1deb9869a6d07ba713136a5` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_static_s174.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_static_s174.json) | other | 40471 | `cb5a14a08dca7a88f72c266bedea87a331ec3ccabdad64b6236fe7eaf01b7b9e` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_static_s175.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_static_s175.json) | other | 38769 | `d5fe7c90394ca9d19b2f2f0abb998d89223316591cf156aca4e246d0819524bb` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_static_s176.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_static_s176.json) | other | 31456 | `71e872792d864b282627c9ba968a7dbc115186f7ee5dd2e0016d9ae361bee785` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_static_s177.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_static_s177.json) | other | 27600 | `5925696656b22c16d3df2ff753df890dcc85690f605b3f131744bd236d7afb54` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_static_s178.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_static_s178.json) | other | 49613 | `8c66fc1a301df960d06ad0a2b43098eb31fbbbb345dea0259bd0ae1599ef97c4` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_static_s179.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_static_s179.json) | other | 26100 | `5a00552cf21bf92f0af655bea3ccffaa32330f075ef59152b43e6dc00214d2d7` |
| [`morphogenesis/experiments/L1_field/x56_dt0.5_static_s180.json`](../morphogenesis/experiments/L1_field/x56_dt0.5_static_s180.json) | other | 40314 | `e4802e9f145583837c2810d19b6be55ba0b062180c84dd190d90789f218fe703` |
| [`morphogenesis/experiments/L1_field/x56_dt2.0_homog_s171.json`](../morphogenesis/experiments/L1_field/x56_dt2.0_homog_s171.json) | other | 5787 | `46630de9dfc56fc11fbd9c4ad18d868c24970ee2af56829ab33378bb58d98bdb` |
| [`morphogenesis/experiments/L1_field/x56_dt2.0_homog_s172.json`](../morphogenesis/experiments/L1_field/x56_dt2.0_homog_s172.json) | other | 5787 | `610c52923771a1ca6dd5b1c4d3ef01977d3f0c1fe3cfc6da63e29a8f7517c627` |
| [`morphogenesis/experiments/L1_field/x56_dt2.0_homog_s173.json`](../morphogenesis/experiments/L1_field/x56_dt2.0_homog_s173.json) | other | 5787 | `f54de4b1b6a5a13271fc298baafb4d713f17820b86aa619b03456d4c2a641473` |
| [`morphogenesis/experiments/L1_field/x56_dt2.0_homog_s174.json`](../morphogenesis/experiments/L1_field/x56_dt2.0_homog_s174.json) | other | 5787 | `dff28f78bf69076ab272d4c72ef14e2368c0f74345f0ce1c13ecebe3f4a495fd` |
| [`morphogenesis/experiments/L1_field/x56_dt2.0_homog_s175.json`](../morphogenesis/experiments/L1_field/x56_dt2.0_homog_s175.json) | other | 5786 | `119abb9faf1d021457ae72b141ee033e9fd4bd2c03d21fe4f69067916110f72b` |
| [`morphogenesis/experiments/L1_field/x56_dt2.0_static_s171.json`](../morphogenesis/experiments/L1_field/x56_dt2.0_static_s171.json) | other | 5838 | `04ebb436384583379cf09ecd9c9eb634a56a7a83bee2182457a534e75eb43907` |
| [`morphogenesis/experiments/L1_field/x56_dt2.0_static_s172.json`](../morphogenesis/experiments/L1_field/x56_dt2.0_static_s172.json) | other | 5838 | `4f0710fa6af69ed64a5466765403fc63910e29a6374952d4040293c655cedc37` |
| [`morphogenesis/experiments/L1_field/x56_dt2.0_static_s173.json`](../morphogenesis/experiments/L1_field/x56_dt2.0_static_s173.json) | other | 5838 | `6858a68201d0467f7c0087c536e731fbf4424bc054f81620d4b609ade64f1713` |
| [`morphogenesis/experiments/L1_field/x56_dt2.0_static_s174.json`](../morphogenesis/experiments/L1_field/x56_dt2.0_static_s174.json) | other | 5838 | `9c52e0ef36a44cf7380c9a4a3cf722ed82cdec5844fa7b6bd5b77fce6fd2b222` |
| [`morphogenesis/experiments/L1_field/x56_dt2.0_static_s175.json`](../morphogenesis/experiments/L1_field/x56_dt2.0_static_s175.json) | other | 5838 | `96c1421e24b4140b817e0cfa393a0229ad07285949184a6514106d1a374484ba` |
| [`morphogenesis/experiments/L1_field/x58_homog_s171.json`](../morphogenesis/experiments/L1_field/x58_homog_s171.json) | other | 13455 | `39f005abe52cfb6e9945b7767c8fc3b2a909d39a6f6d9fe1320f2f69dc8aa821` |
| [`morphogenesis/experiments/L1_field/x58_homog_s172.json`](../morphogenesis/experiments/L1_field/x58_homog_s172.json) | other | 15013 | `828c9ee12dbc432edf0aff39cfa49b4bd0cd96120e9373e03be3301fc5ee10ba` |
| [`morphogenesis/experiments/L1_field/x58_homog_s173.json`](../morphogenesis/experiments/L1_field/x58_homog_s173.json) | other | 13433 | `249d6b8df62190ab2f80b059a46c13d7dbaf94ce4fecfa230b6e0a5dc4eed848` |
| [`morphogenesis/experiments/L1_field/x58_homog_s174.json`](../morphogenesis/experiments/L1_field/x58_homog_s174.json) | other | 13876 | `edbc573b93a9cced7a24635e9b3c24b38d9c6895ca14fb8f52a6ebe1b0c73fe6` |
| [`morphogenesis/experiments/L1_field/x58_homog_s175.json`](../morphogenesis/experiments/L1_field/x58_homog_s175.json) | other | 15324 | `5b44d08ab5806e328d34a25276a7e6e3052b992afcc7aefdb376e13fe525fb12` |
| [`morphogenesis/experiments/L1_field/x58_pattern_s171.json`](../morphogenesis/experiments/L1_field/x58_pattern_s171.json) | other | 22209 | `e00afe14ce3f87d479f749c97651318ee688f2f497f708c26bf7d82a85f5515f` |
| [`morphogenesis/experiments/L1_field/x58_pattern_s172.json`](../morphogenesis/experiments/L1_field/x58_pattern_s172.json) | other | 15814 | `728560e830f415564687a462388b718c19fee1896fcb1acc056ba119d7b91249` |
| [`morphogenesis/experiments/L1_field/x58_pattern_s173.json`](../morphogenesis/experiments/L1_field/x58_pattern_s173.json) | other | 30493 | `9c1f7250d27be2d44e2041fdedad7fea5193ca15cc0e7f5a5b603d68babd4904` |
| [`morphogenesis/experiments/L1_field/x58_pattern_s174.json`](../morphogenesis/experiments/L1_field/x58_pattern_s174.json) | other | 15917 | `3c2cc415380569e735b5e7d1c9b0d0ccf5f85ac6592eb6d6558db47cdda19a2b` |
| [`morphogenesis/experiments/L1_field/x58_pattern_s175.json`](../morphogenesis/experiments/L1_field/x58_pattern_s175.json) | other | 13639 | `411dd1089aed63e7dfccd56450b4fb9135137094c79b28219f7f4e053756d201` |
| [`morphogenesis/experiments/L1_field/x58_series_index.json`](../morphogenesis/experiments/L1_field/x58_series_index.json) | other | 1999 | `b0b7be4326ef506175de0fce8b060f71879c4a378074ed66d2946354690c63f8` |
| [`morphogenesis/experiments/L1_field/x59_a10_s171.json`](../morphogenesis/experiments/L1_field/x59_a10_s171.json) | other | 8044 | `0de7dc6389d7bfe023e08d82056bca9ab6151d79715a3dc4140a84dc5f62a6f9` |
| [`morphogenesis/experiments/L1_field/x59_a10_s172.json`](../morphogenesis/experiments/L1_field/x59_a10_s172.json) | other | 9476 | `7e92aa0421e992e77c0ae854398298d71f203b09b6abbbc496b15c00af39b362` |
| [`morphogenesis/experiments/L1_field/x59_a10_s173.json`](../morphogenesis/experiments/L1_field/x59_a10_s173.json) | other | 8754 | `9c0745364453e39e2280835a279ad918ba705a07a3d9b213bbe7f83201aaddac` |
| [`morphogenesis/experiments/L1_field/x59_a10_s174.json`](../morphogenesis/experiments/L1_field/x59_a10_s174.json) | other | 9706 | `5415c1b97df0d8f0c63562c20a3258eb1b661c09e82c0b9e14cf12f0a60aef47` |
| [`morphogenesis/experiments/L1_field/x59_a10_s175.json`](../morphogenesis/experiments/L1_field/x59_a10_s175.json) | other | 8032 | `d3153745097c2fc5557585d9f2bccd2fb4752078fc4005b7ed70dae2b4a3485d` |
| [`morphogenesis/experiments/L1_field/x59_a25_s171.json`](../morphogenesis/experiments/L1_field/x59_a25_s171.json) | other | 8185 | `255c84b357487d533981c7a0ae3f547f2e03c2eff4a1d88fa9db258bce82f413` |
| [`morphogenesis/experiments/L1_field/x59_a25_s172.json`](../morphogenesis/experiments/L1_field/x59_a25_s172.json) | other | 8899 | `de1aceaf6bf1ffcada13880040950fb5d7986d0cf065790adb86d14c0c7d5dd3` |
| [`morphogenesis/experiments/L1_field/x59_a25_s173.json`](../morphogenesis/experiments/L1_field/x59_a25_s173.json) | other | 9879 | `fd940722bdbb194245317f36c853e4086f4ffc13a8d3121cfdd418074be00dd8` |
| [`morphogenesis/experiments/L1_field/x59_a25_s174.json`](../morphogenesis/experiments/L1_field/x59_a25_s174.json) | other | 14434 | `b25972a03de8760063bf8a71fcfa6b062f7108e91b827cd4881f990e236e5dfa` |
| [`morphogenesis/experiments/L1_field/x59_a25_s175.json`](../morphogenesis/experiments/L1_field/x59_a25_s175.json) | other | 11189 | `92d2b5527c3d2c5a6610da432553ab62fab08e7673a13cafaec46a943d31f63b` |
| [`morphogenesis/experiments/L1_field/x59_a50_s171.json`](../morphogenesis/experiments/L1_field/x59_a50_s171.json) | other | 15583 | `0d8eeb90d125972607290a337de0714eb037606a7a6f9a375245b04d24d2dad8` |
| [`morphogenesis/experiments/L1_field/x59_a50_s172.json`](../morphogenesis/experiments/L1_field/x59_a50_s172.json) | other | 23526 | `4b5ee258165d56015b98a30c397108b024f55227e7778bf822315cc1f596c25a` |
| [`morphogenesis/experiments/L1_field/x59_a50_s173.json`](../morphogenesis/experiments/L1_field/x59_a50_s173.json) | other | 12012 | `919ef5a00defc6273e62bf5dfd5429f95b678f7e9565a083486bf53483d302f7` |
| [`morphogenesis/experiments/L1_field/x59_a50_s174.json`](../morphogenesis/experiments/L1_field/x59_a50_s174.json) | other | 12679 | `acb74b8476fae48b80690c0cb8c8a01162b309c97b5796c7eda72b6364ca1a5d` |
| [`morphogenesis/experiments/L1_field/x59_a50_s175.json`](../morphogenesis/experiments/L1_field/x59_a50_s175.json) | other | 10862 | `64a83f6abc0a3805d40ad7c3764c5411a60515a0988d72063098779d251b2d9b` |
| [`morphogenesis/experiments/L1_field/x59_series_index.json`](../morphogenesis/experiments/L1_field/x59_series_index.json) | other | 1789 | `30b2aca1b15fbe4d4d6b77ee7c350d03dae52dca385dc3fd4745c1a9d036ba78` |
| [`morphogenesis/experiments/L1_field/x60_homog_s171.json`](../morphogenesis/experiments/L1_field/x60_homog_s171.json) | other | 9280 | `97769dc50ac6fe176afe94a39512c3eae955d66f4aef997faa9d8869acde813c` |
| [`morphogenesis/experiments/L1_field/x60_homog_s172.json`](../morphogenesis/experiments/L1_field/x60_homog_s172.json) | other | 9422 | `532272cc3dbc0dce4ce17e14da373f94744bf976ad9433a9e9b0282ac7392843` |
| [`morphogenesis/experiments/L1_field/x60_homog_s173.json`](../morphogenesis/experiments/L1_field/x60_homog_s173.json) | other | 8410 | `3cee049222c8045e634ec618de952c194b701e6ba27198b43a1ecab084f8dbd3` |
| [`morphogenesis/experiments/L1_field/x60_homog_s174.json`](../morphogenesis/experiments/L1_field/x60_homog_s174.json) | other | 10564 | `47e0f772da1072a6388e97189778f28d9583c56ca7987fc746f59aa393d6a384` |
| [`morphogenesis/experiments/L1_field/x60_homog_s175.json`](../morphogenesis/experiments/L1_field/x60_homog_s175.json) | other | 8550 | `3dee7a73e2a0325c92c55b788b10a1c0ed683a2471137cc037108d84c82169fb` |
| [`morphogenesis/experiments/L1_field/x60_homog_s176.json`](../morphogenesis/experiments/L1_field/x60_homog_s176.json) | other | 10535 | `e26eff3ad078596727598e0bbd58b28678e80bdfb7bce083a8cd79f81e6d1615` |
| [`morphogenesis/experiments/L1_field/x60_homog_s177.json`](../morphogenesis/experiments/L1_field/x60_homog_s177.json) | other | 8707 | `ed8cee16bcafa81c01a8fd6297285cc31e6b27e01303501ac7e8ce5a9cf32910` |
| [`morphogenesis/experiments/L1_field/x60_homog_s178.json`](../morphogenesis/experiments/L1_field/x60_homog_s178.json) | other | 11438 | `6082116fc221abbb084755a07fde8dac05df316ec0e3a5b5dc86b7972dd26968` |
| [`morphogenesis/experiments/L1_field/x60_homog_s179.json`](../morphogenesis/experiments/L1_field/x60_homog_s179.json) | other | 9145 | `4ee4511ca474a322c7a326fc64966a8d1ef4a4981dd02731a3bdde9359e61b8c` |
| [`morphogenesis/experiments/L1_field/x60_homog_s180.json`](../morphogenesis/experiments/L1_field/x60_homog_s180.json) | other | 8562 | `7d2bbbeced72036cd7a0a06b765559ec0fe110b8dd7297a3dbcf15d7f6d92ecb` |
| [`morphogenesis/experiments/L1_field/x60_pattern_s171.json`](../morphogenesis/experiments/L1_field/x60_pattern_s171.json) | other | 15610 | `2f1e21b4e7153f16ed220b7a1e129c6e1b4ba7aef5399d132da3f76e8f3b40ef` |
| [`morphogenesis/experiments/L1_field/x60_pattern_s172.json`](../morphogenesis/experiments/L1_field/x60_pattern_s172.json) | other | 23538 | `3a8e0ad544cb01a014c27911e8da3907cd874fedb5ae7cb8692c632250f82d91` |
| [`morphogenesis/experiments/L1_field/x60_pattern_s173.json`](../morphogenesis/experiments/L1_field/x60_pattern_s173.json) | other | 12024 | `6bfd67ac855b791af1728100d5529b8abe31fbfce9dd63f0de647a71bfb2a944` |
| [`morphogenesis/experiments/L1_field/x60_pattern_s174.json`](../morphogenesis/experiments/L1_field/x60_pattern_s174.json) | other | 12691 | `d1f3ad9e7c466534e99312cd080b4b2ce763006ddabb694bc9efcad0c72c78fe` |
| [`morphogenesis/experiments/L1_field/x60_pattern_s175.json`](../morphogenesis/experiments/L1_field/x60_pattern_s175.json) | other | 10874 | `fd40390e7cd41bc4a58425e05d798b5ca89d7c84c3c85483408df7d2aa2e29fe` |
| [`morphogenesis/experiments/L1_field/x60_pattern_s176.json`](../morphogenesis/experiments/L1_field/x60_pattern_s176.json) | other | 18965 | `bc84de4cd2c937519e644df6a484d42d70641de35cd535ad10ada020d0a92eab` |
| [`morphogenesis/experiments/L1_field/x60_pattern_s177.json`](../morphogenesis/experiments/L1_field/x60_pattern_s177.json) | other | 12044 | `7f19362e6fc8efb61d9afe26020f5b25b98d170b3ed1daab08e86f33ad237a59` |
| [`morphogenesis/experiments/L1_field/x60_pattern_s178.json`](../morphogenesis/experiments/L1_field/x60_pattern_s178.json) | other | 17480 | `95522d03814d7ce37be73d6620f6efa1b48e80f1d61f8eab5176cb7fa3acb7f7` |
| [`morphogenesis/experiments/L1_field/x60_pattern_s179.json`](../morphogenesis/experiments/L1_field/x60_pattern_s179.json) | other | 11448 | `b528df3c101345d601b6a64a32e9ef30de6904b85cbfcd918e593d8249c5df84` |
| [`morphogenesis/experiments/L1_field/x60_pattern_s180.json`](../morphogenesis/experiments/L1_field/x60_pattern_s180.json) | other | 14291 | `bd1bafe8a55bb33749cb45f716f9d4773cfab0c69ec10c96fa8ed7477ad17858` |
| [`morphogenesis/experiments/L1_field/x60_series_index.json`](../morphogenesis/experiments/L1_field/x60_series_index.json) | other | 3824 | `d1b6eeeca9cd21f8b7fe6c1ada2e05a5522c031e5f161f1825b8af46e2087604` |
| [`morphogenesis/experiments/L1_field/x61l_a50_s171.json`](../morphogenesis/experiments/L1_field/x61l_a50_s171.json) | other | 34536 | `a0a6ed9269a8a5043c08e36ea2e357a194b670046df6554220a49c253e3fec76` |
| [`morphogenesis/experiments/L1_field/x61l_a50_s172.json`](../morphogenesis/experiments/L1_field/x61l_a50_s172.json) | other | 58268 | `83f25f253482110c62787a59cb1daeaeb50344b0a471983de0fdc1fa8edbc4c8` |
| [`morphogenesis/experiments/L1_field/x61l_a50_s173.json`](../morphogenesis/experiments/L1_field/x61l_a50_s173.json) | other | 25880 | `5a33c02fa995e2ca49d7340e84a0a5d77dc92467cb6521f36acaf2b06406718f` |
| [`morphogenesis/experiments/L1_field/x61l_a50_s174.json`](../morphogenesis/experiments/L1_field/x61l_a50_s174.json) | other | 43094 | `c32a8607e64385b6349cace92f8bb8085089b4f2aa942da62434022818fcd4b5` |
| [`morphogenesis/experiments/L1_field/x61l_a50_s175.json`](../morphogenesis/experiments/L1_field/x61l_a50_s175.json) | other | 24647 | `0d22663ddbb73ece1e19194ccdce598b938e15f9b2e0b845517837356c8a39eb` |
| [`morphogenesis/experiments/L1_field/x61l_series_index.json`](../morphogenesis/experiments/L1_field/x61l_series_index.json) | other | 535 | `ebeb88d5cdb7d124167f0c66dcfa78fd152b687e050065b526b7da0f4a64d611` |
| [`morphogenesis/experiments/L1_field/x62_s04_s171.json`](../morphogenesis/experiments/L1_field/x62_s04_s171.json) | other | 8620 | `79a8c094845b9d212fb16ca54c50ddbd8729a220af9b15c9cf29095f7500e268` |
| [`morphogenesis/experiments/L1_field/x62_s04_s172.json`](../morphogenesis/experiments/L1_field/x62_s04_s172.json) | other | 8315 | `640b5fae4bfe019106c166cbe7ec7fa9cf6688f028601a0b3cff21da517f41ee` |
| [`morphogenesis/experiments/L1_field/x62_s04_s173.json`](../morphogenesis/experiments/L1_field/x62_s04_s173.json) | other | 8472 | `1651cac075ccb8ccec1fb670fc5282efe0d4f00783f800ab225b5bcb5da86b5b` |
| [`morphogenesis/experiments/L1_field/x62_s04_s174.json`](../morphogenesis/experiments/L1_field/x62_s04_s174.json) | other | 12032 | `0aa2c6e791194a7b54d56044ae4dd58ed59cc2cdebd827939114ec2b1929e6d0` |
| [`morphogenesis/experiments/L1_field/x62_s04_s175.json`](../morphogenesis/experiments/L1_field/x62_s04_s175.json) | other | 8016 | `02c1721279c5b9f04a17dc44016dbb33840147c3be89bfc491f21ec2ebf7e115` |
| [`morphogenesis/experiments/L1_field/x62_s12_s171.json`](../morphogenesis/experiments/L1_field/x62_s12_s171.json) | other | 15583 | `101c20f66214ff4469b32e972393c38a1bd564f7e77315d438bee3361ccf64f7` |
| [`morphogenesis/experiments/L1_field/x62_s12_s172.json`](../morphogenesis/experiments/L1_field/x62_s12_s172.json) | other | 23526 | `ffc74a1e7faea60316c529b525ecb8accc8d0882aa1239d207858025d8c0d10a` |
| [`morphogenesis/experiments/L1_field/x62_s12_s173.json`](../morphogenesis/experiments/L1_field/x62_s12_s173.json) | other | 12012 | `506aceba290b24c6ef6b1474cd7bbefee65e6fafcad28f1f3deb3bae42ecb5c4` |
| [`morphogenesis/experiments/L1_field/x62_s12_s174.json`](../morphogenesis/experiments/L1_field/x62_s12_s174.json) | other | 12679 | `94eaddbfd476d273583f3014a20146115310d794d065445b8ac13ac5e207f66e` |
| [`morphogenesis/experiments/L1_field/x62_s12_s175.json`](../morphogenesis/experiments/L1_field/x62_s12_s175.json) | other | 10862 | `6b4aebd09cab3216a80d5908b6301232b1ef478637d3384ef5fcd16738dce73d` |
| [`morphogenesis/experiments/L1_field/x62_s24_s171.json`](../morphogenesis/experiments/L1_field/x62_s24_s171.json) | other | 11461 | `9c53fa535a0af7f227670e5d6052642debf826764f485c9e6298da8efb094e8d` |
| [`morphogenesis/experiments/L1_field/x62_s24_s172.json`](../morphogenesis/experiments/L1_field/x62_s24_s172.json) | other | 9041 | `e9b22d3e8769c48ec964fd4940613ad8c6a4112c701e3ff2ecab5942d598d9ae` |
| [`morphogenesis/experiments/L1_field/x62_s24_s173.json`](../morphogenesis/experiments/L1_field/x62_s24_s173.json) | other | 14464 | `7aa0b7661167c25874e565c4ee8da04badedc10aa4446c0db1ccb36fd92619d9` |
| [`morphogenesis/experiments/L1_field/x62_s24_s174.json`](../morphogenesis/experiments/L1_field/x62_s24_s174.json) | other | 13348 | `01e645a1cb97e493e5568fb38ebb3e99ed48e2d95c42cf2cae7bf7ee1cb5dc02` |
| [`morphogenesis/experiments/L1_field/x62_s24_s175.json`](../morphogenesis/experiments/L1_field/x62_s24_s175.json) | other | 11348 | `87789d0f7749318d7e3a0e10340e58f8b9058aa5f80808a1dfd71fcc7d013660` |
| [`morphogenesis/experiments/L1_field/x62_series_index.json`](../morphogenesis/experiments/L1_field/x62_series_index.json) | other | 1789 | `a6f3251c5efaf389699e6d26893ce1badfb655c10738f3fa3824206485718614` |
| [`morphogenesis/experiments/L1_field/x63_s06_s171.json`](../morphogenesis/experiments/L1_field/x63_s06_s171.json) | other | 8187 | `2fbba5b2c43b4b416e7ad9e73804e9837824bdd25bfc698b06e08e5efb54b4b5` |
| [`morphogenesis/experiments/L1_field/x63_s06_s172.json`](../morphogenesis/experiments/L1_field/x63_s06_s172.json) | other | 8482 | `1de1b8feda0da29a68c6b535570c2b9de1696adcee57e1a2d104594fe9a6bffd` |
| [`morphogenesis/experiments/L1_field/x63_s06_s173.json`](../morphogenesis/experiments/L1_field/x63_s06_s173.json) | other | 10726 | `6951edefafabebb8ff5bb7689205fbf9b92e69303d5b511f0339d05ce36f2722` |
| [`morphogenesis/experiments/L1_field/x63_s06_s174.json`](../morphogenesis/experiments/L1_field/x63_s06_s174.json) | other | 8883 | `ccafa70be3d7463ce67c12662cd67f3d1966ad5fbcc3e7148dedcd13ba75fc25` |
| [`morphogenesis/experiments/L1_field/x63_s06_s175.json`](../morphogenesis/experiments/L1_field/x63_s06_s175.json) | other | 9616 | `8ded6304aafb26a9c1ff3c916c45243e37f67c172d9dee4f6ce7bc2ecb5dcd17` |
| [`morphogenesis/experiments/L1_field/x63_s08_s171.json`](../morphogenesis/experiments/L1_field/x63_s08_s171.json) | other | 10187 | `538423023a430bd38bc330f79ba21f8b2258c2dd9039d5c4563809ecec2d9260` |
| [`morphogenesis/experiments/L1_field/x63_s08_s172.json`](../morphogenesis/experiments/L1_field/x63_s08_s172.json) | other | 14751 | `8850c90392b1063d154e383c57d8e63fc4bad8b49f36a75d7f660989aa688dc4` |
| [`morphogenesis/experiments/L1_field/x63_s08_s173.json`](../morphogenesis/experiments/L1_field/x63_s08_s173.json) | other | 8473 | `3991852db9a52250b8cd1bf5c5b8c74412f4214987f3270b16ad4e51728b1156` |
| [`morphogenesis/experiments/L1_field/x63_s08_s174.json`](../morphogenesis/experiments/L1_field/x63_s08_s174.json) | other | 10714 | `4c2483a3fbf9ce610a0eb0b76be2a8a34c98e9942a7498c1810bb53008c95bfc` |
| [`morphogenesis/experiments/L1_field/x63_s08_s175.json`](../morphogenesis/experiments/L1_field/x63_s08_s175.json) | other | 8043 | `c52754abb713de555c6c7d7b23d8e97ce51d719edd98f115482838bb8657c5ce` |
| [`morphogenesis/experiments/L1_field/x63_s16_s171.json`](../morphogenesis/experiments/L1_field/x63_s16_s171.json) | other | 10460 | `4b135137dc9d731acb41219e0d0d481bcf8b292e977ebc1c60f66eb628d4a4b2` |
| [`morphogenesis/experiments/L1_field/x63_s16_s172.json`](../morphogenesis/experiments/L1_field/x63_s16_s172.json) | other | 15152 | `54e4e3fe61d4714e3c5e4570ee04b029141ba0130b53da98244a7be907ad4fb3` |
| [`morphogenesis/experiments/L1_field/x63_s16_s173.json`](../morphogenesis/experiments/L1_field/x63_s16_s173.json) | other | 13771 | `f1fcdf759e18708a8edf74e03c03a2acc7859cb64642a9a45c3e049d3123800d` |
| [`morphogenesis/experiments/L1_field/x63_s16_s174.json`](../morphogenesis/experiments/L1_field/x63_s16_s174.json) | other | 25541 | `28760a8682c8479d03dc3df658d5ee1d0b114bf3b1cc710cec58470c73d8b68a` |
| [`morphogenesis/experiments/L1_field/x63_s16_s175.json`](../morphogenesis/experiments/L1_field/x63_s16_s175.json) | other | 9178 | `960bb721dcaa932c47e7df076e59711304971c95030b4e5677a26838e64512ce` |
| [`morphogenesis/experiments/L1_field/x63_s32_s171.json`](../morphogenesis/experiments/L1_field/x63_s32_s171.json) | other | 9211 | `4e7ebc7e5764387bf37323fefb0dde464f631ce710587c27c04f5fca81ad7269` |
| [`morphogenesis/experiments/L1_field/x63_s32_s172.json`](../morphogenesis/experiments/L1_field/x63_s32_s172.json) | other | 8934 | `80de7c006904d0036cc60ed7434eef7832eaa662ae64aa465cc8a81bf8c2cec3` |
| [`morphogenesis/experiments/L1_field/x63_s32_s173.json`](../morphogenesis/experiments/L1_field/x63_s32_s173.json) | other | 9345 | `c15869ae7b67d70aad5a019ce71adac394af3f7604e6bc9f09b8e7847c03308c` |
| [`morphogenesis/experiments/L1_field/x63_s32_s174.json`](../morphogenesis/experiments/L1_field/x63_s32_s174.json) | other | 16048 | `1dff67269a1022b538fd1e252abcfcfe5474b50eca987b5af5046a2de6526023` |
| [`morphogenesis/experiments/L1_field/x63_s32_s175.json`](../morphogenesis/experiments/L1_field/x63_s32_s175.json) | other | 12496 | `5a62db3a728a8e9b4385aff0a2b3f8131904c77afad3347cbdc531152d5ff9ae` |
| [`morphogenesis/experiments/L1_field/x63_series_index.json`](../morphogenesis/experiments/L1_field/x63_series_index.json) | other | 2369 | `9b5bcab87ca7d8f1d4c63d256b8815c05a66d93e797196a73323c866017c0cbc` |
| [`morphogenesis/experiments/L1_field/x64_homog_s171.json`](../morphogenesis/experiments/L1_field/x64_homog_s171.json) | other | 12574 | `51e4db442da444c9d2f6566f37f4bb71a93cbf0b0d81941482c32dcfe3d3e164` |
| [`morphogenesis/experiments/L1_field/x64_homog_s172.json`](../morphogenesis/experiments/L1_field/x64_homog_s172.json) | other | 13743 | `4f87c2101f9bdcfd9096b7ab1b608177d20b951ca87d86c4328aa8d167fab644` |
| [`morphogenesis/experiments/L1_field/x64_homog_s173.json`](../morphogenesis/experiments/L1_field/x64_homog_s173.json) | other | 15342 | `56dd83b687b99fd552fe2ed626bed1c2903aaa625b41f3515146a7ace695701f` |
| [`morphogenesis/experiments/L1_field/x64_homog_s174.json`](../morphogenesis/experiments/L1_field/x64_homog_s174.json) | other | 15341 | `5e3e66e62e3266fa55d0514d15078ea7eb6e30386093e047eba3dea6d4ce885d` |
| [`morphogenesis/experiments/L1_field/x64_homog_s175.json`](../morphogenesis/experiments/L1_field/x64_homog_s175.json) | other | 14043 | `411aec63c02592204cb6731647d7f07ef67126f066c48928a224c7efd821014b` |
| [`morphogenesis/experiments/L1_field/x64_pattern_s171.json`](../morphogenesis/experiments/L1_field/x64_pattern_s171.json) | other | 17252 | `104c8b2f2ac237c0844ea3eca37efa5597e8075c234d13838e90987f7bd0472f` |
| [`morphogenesis/experiments/L1_field/x64_pattern_s172.json`](../morphogenesis/experiments/L1_field/x64_pattern_s172.json) | other | 16174 | `7b6e1277a2acb6f89c9a782bb8000029602061478a4901fb21381c3613c4dd2b` |
| [`morphogenesis/experiments/L1_field/x64_pattern_s173.json`](../morphogenesis/experiments/L1_field/x64_pattern_s173.json) | other | 15833 | `46e5363c7596a957b36bafb773c89038af255fb55f67220c238655ed5c274dd1` |
| [`morphogenesis/experiments/L1_field/x64_pattern_s174.json`](../morphogenesis/experiments/L1_field/x64_pattern_s174.json) | other | 20592 | `b0be8d973d15f19a830431d776697ff1ea75c5f4412ec4115e2f7e168d3cacd4` |
| [`morphogenesis/experiments/L1_field/x64_pattern_s175.json`](../morphogenesis/experiments/L1_field/x64_pattern_s175.json) | other | 18593 | `752af51a4b6733b7e21f75ed399f6a0ba1d506540d26a10f5ff3aa8861f35300` |
| [`morphogenesis/experiments/L1_field/x64_series_index.json`](../morphogenesis/experiments/L1_field/x64_series_index.json) | other | 1249 | `2a16244f1409ff23e61c9584550649f7b892d2b3d954c749217255d0537d8f21` |
| [`morphogenesis/experiments/L1_field/x65_homog_s171.json`](../morphogenesis/experiments/L1_field/x65_homog_s171.json) | other | 13026 | `8070cc6b59eefa3c5e658601a94e7bbb0885d636946b3d3b76790aee4ff090a0` |
| [`morphogenesis/experiments/L1_field/x65_homog_s172.json`](../morphogenesis/experiments/L1_field/x65_homog_s172.json) | other | 19112 | `3fa3dba7d4f7e072cd69d2be259ead42302c182aaa8dcd7f86b36881645fa016` |
| [`morphogenesis/experiments/L1_field/x65_homog_s173.json`](../morphogenesis/experiments/L1_field/x65_homog_s173.json) | other | 12846 | `29e94a57a152755ffd615cebbc1fcf316a4ab2a0e789899fc00904575b3c87af` |
| [`morphogenesis/experiments/L1_field/x65_homog_s174.json`](../morphogenesis/experiments/L1_field/x65_homog_s174.json) | other | 12414 | `d131eb737acb299ec4ea4f6d841ab1d1bcf053fb0b4fae789733d9b20a794738` |
| [`morphogenesis/experiments/L1_field/x65_homog_s175.json`](../morphogenesis/experiments/L1_field/x65_homog_s175.json) | other | 12421 | `b76f7eb1ba0efc649d576048acc242032b67a5b2cf1b1f3b8f301dbff5875a30` |
| [`morphogenesis/experiments/L1_field/x65_pattern_s171.json`](../morphogenesis/experiments/L1_field/x65_pattern_s171.json) | other | 19417 | `43b196633832bf5bd8aa70c947f663f3fd86f8b9db11894952d4ca8e3b7d3d95` |
| [`morphogenesis/experiments/L1_field/x65_pattern_s172.json`](../morphogenesis/experiments/L1_field/x65_pattern_s172.json) | other | 13916 | `d5374ac0d1dd2c81beced3b69a42a18bb75382713a9c569e2e9d40b4d521daf6` |
| [`morphogenesis/experiments/L1_field/x65_pattern_s173.json`](../morphogenesis/experiments/L1_field/x65_pattern_s173.json) | other | 17212 | `66e779653f8aeee7e8fd82d723b6fd81dc73cfa3c6b37cfdbde7177e4689d5ae` |
| [`morphogenesis/experiments/L1_field/x65_pattern_s174.json`](../morphogenesis/experiments/L1_field/x65_pattern_s174.json) | other | 18027 | `ccaa2d38dadee3c5ca1a4ab85d05db8136f97a472ea8dc85340f94118bd8d7d0` |
| [`morphogenesis/experiments/L1_field/x65_pattern_s175.json`](../morphogenesis/experiments/L1_field/x65_pattern_s175.json) | other | 13627 | `c35f094fe5b164dbe7614358ad36ebbbbbd8dc1a08e28335d58523bcb4ae6309` |
| [`morphogenesis/experiments/L1_field/x65_series_index.json`](../morphogenesis/experiments/L1_field/x65_series_index.json) | other | 1249 | `3698894b696efc881b718bbf32bd8056d510b5c47f8073607bcce4937cde5a74` |
| [`morphogenesis/experiments/L1_field/x66_g096_homog_s171.json`](../morphogenesis/experiments/L1_field/x66_g096_homog_s171.json) | other | 17008 | `b9bb210875aaa9128016adea06f7a86e62662d11a23ae68a7a6bee0e5b594113` |
| [`morphogenesis/experiments/L1_field/x66_g096_homog_s172.json`](../morphogenesis/experiments/L1_field/x66_g096_homog_s172.json) | other | 17003 | `d4811f691efb153e7ad1ec2f5c4801d8a8b5b03133e0b7794b9a4110663c39cd` |
| [`morphogenesis/experiments/L1_field/x66_g096_homog_s173.json`](../morphogenesis/experiments/L1_field/x66_g096_homog_s173.json) | other | 13425 | `d2c73faea7369cb1d83eef9850f456d71325b25702d0670c63867f2aea7d8c06` |
| [`morphogenesis/experiments/L1_field/x66_g096_homog_s174.json`](../morphogenesis/experiments/L1_field/x66_g096_homog_s174.json) | other | 13573 | `f2944efd538903dfc1b128f11e990711656980b95bd07ff4c0d6ac3e6713f685` |
| [`morphogenesis/experiments/L1_field/x66_g096_homog_s175.json`](../morphogenesis/experiments/L1_field/x66_g096_homog_s175.json) | other | 21966 | `a94b713452a4e31066062df212d9e3e773605fc058432a8455476569149e079b` |
| [`morphogenesis/experiments/L1_field/x66_g096_pattern_s171.json`](../morphogenesis/experiments/L1_field/x66_g096_pattern_s171.json) | other | 12329 | `be79ebe9a95d75452033d68ea1b985fba94639b0406aadf405c34c6f91971301` |
| [`morphogenesis/experiments/L1_field/x66_g096_pattern_s172.json`](../morphogenesis/experiments/L1_field/x66_g096_pattern_s172.json) | other | 15622 | `e31e05daaf1758cb7dd203010b07082382774b0028aad39b7f600683bc57544c` |
| [`morphogenesis/experiments/L1_field/x66_g096_pattern_s173.json`](../morphogenesis/experiments/L1_field/x66_g096_pattern_s173.json) | other | 16766 | `6bd0487f340d78cab16627518dec71d37701c165745acc2d91906a61dbd08cbc` |
| [`morphogenesis/experiments/L1_field/x66_g096_pattern_s174.json`](../morphogenesis/experiments/L1_field/x66_g096_pattern_s174.json) | other | 27288 | `a0331bb3bf9ba36f0e0a05ebf10d45007fa287d0564becb0aeecea8f7f29eaa2` |
| [`morphogenesis/experiments/L1_field/x66_g096_pattern_s175.json`](../morphogenesis/experiments/L1_field/x66_g096_pattern_s175.json) | other | 24592 | `c2f6020eeed9f072db868126c9a4d176e4b863ca61f94e9a8ec91db3e341859f` |
| [`morphogenesis/experiments/L1_field/x66_g108_homog_s171.json`](../morphogenesis/experiments/L1_field/x66_g108_homog_s171.json) | other | 12598 | `0d76dd002494001cae721904db627983c2efee882531717c4e9e438e88164759` |
| [`morphogenesis/experiments/L1_field/x66_g108_homog_s172.json`](../morphogenesis/experiments/L1_field/x66_g108_homog_s172.json) | other | 18161 | `4d4169dc61bcff073082fa09735cc61adde55415895f1560e7cd85f9d0287bf1` |
| [`morphogenesis/experiments/L1_field/x66_g108_homog_s173.json`](../morphogenesis/experiments/L1_field/x66_g108_homog_s173.json) | other | 28051 | `7d4f5f2f5fa8225bae05f5649c79ac3557f036725b7c09aec79cb2a03d203b31` |
| [`morphogenesis/experiments/L1_field/x66_g108_homog_s174.json`](../morphogenesis/experiments/L1_field/x66_g108_homog_s174.json) | other | 20147 | `201ab819be4fad583711440cbd06d0a69268838c26f0e1e078bd19fe9ec41293` |
| [`morphogenesis/experiments/L1_field/x66_g108_homog_s175.json`](../morphogenesis/experiments/L1_field/x66_g108_homog_s175.json) | other | 13722 | `4e5700d8be8f12fbec6f48168d668f578abe8358e03dfb37ccea5d19017cabab` |
| [`morphogenesis/experiments/L1_field/x66_g108_pattern_s171.json`](../morphogenesis/experiments/L1_field/x66_g108_pattern_s171.json) | other | 15481 | `00773dd4314e515f992337a795655133a7a3567fb38ab43336de475b1c65feb9` |
| [`morphogenesis/experiments/L1_field/x66_g108_pattern_s172.json`](../morphogenesis/experiments/L1_field/x66_g108_pattern_s172.json) | other | 12781 | `971624286f03d2ced0f80525a4c97e4f982ac7b54c551bf06977a8b1bf447d48` |
| [`morphogenesis/experiments/L1_field/x66_g108_pattern_s173.json`](../morphogenesis/experiments/L1_field/x66_g108_pattern_s173.json) | other | 16338 | `61138c86bbd286a4f05681f0b0f9ded049d654a377999129e98ce40255712908` |
| [`morphogenesis/experiments/L1_field/x66_g108_pattern_s174.json`](../morphogenesis/experiments/L1_field/x66_g108_pattern_s174.json) | other | 24229 | `926c25db3325ab6d0337d6dac65dcbabb633299dd198f8f406ea6c3e8500c732` |
| [`morphogenesis/experiments/L1_field/x66_g108_pattern_s175.json`](../morphogenesis/experiments/L1_field/x66_g108_pattern_s175.json) | other | 13490 | `de5e0ff172555c93812f289467e6b6568b780ddfdec5e2a56d9d8f31ceef9788` |
| [`morphogenesis/experiments/L1_field/x66_series_index.json`](../morphogenesis/experiments/L1_field/x66_series_index.json) | other | 2488 | `4dfdb06b5c988e50afa74035246ca3e6e87d357ad94d99ee77067349c2d8de7e` |
| [`morphogenesis/experiments/L1_field/x67_homog_s171.json`](../morphogenesis/experiments/L1_field/x67_homog_s171.json) | other | 11323 | `d6704fad8acb7ac2344ab9d7fd3f44c412a10d2b5ff6ab3ffd327135147963a6` |
| [`morphogenesis/experiments/L1_field/x67_homog_s172.json`](../morphogenesis/experiments/L1_field/x67_homog_s172.json) | other | 14335 | `ac2598b1cd2e72060c7cbc0c122edada2f76a0eb80a594b968803e600b570707` |
| [`morphogenesis/experiments/L1_field/x67_homog_s173.json`](../morphogenesis/experiments/L1_field/x67_homog_s173.json) | other | 10171 | `8c18639ebeab6e8598a4f19b0aeb4338ad1b733a7a24740593300db837e12b28` |
| [`morphogenesis/experiments/L1_field/x67_homog_s174.json`](../morphogenesis/experiments/L1_field/x67_homog_s174.json) | other | 11297 | `6994685f65695912247cb83362047f01d82011271a3296386d000640d29d8ced` |
| [`morphogenesis/experiments/L1_field/x67_homog_s175.json`](../morphogenesis/experiments/L1_field/x67_homog_s175.json) | other | 12156 | `9d79ba3650f6153290ff62d71d5120fb032815d2b00f9c2427fa14bc1d0a1adb` |
| [`morphogenesis/experiments/L1_field/x67_pattern_s171.json`](../morphogenesis/experiments/L1_field/x67_pattern_s171.json) | other | 11243 | `98d1eff15988409c98ca98f408cdd2cf71013b401f98e52dceb128eee210605b` |
| [`morphogenesis/experiments/L1_field/x67_pattern_s172.json`](../morphogenesis/experiments/L1_field/x67_pattern_s172.json) | other | 12384 | `f05998cc6b405f76f42c2e577a6a887681a2818f1a54141bea91d52f8ed0ad8e` |
| [`morphogenesis/experiments/L1_field/x67_pattern_s173.json`](../morphogenesis/experiments/L1_field/x67_pattern_s173.json) | other | 23586 | `c51429d9a46a35b812716b7dab167716f77d3b807efa2ea4678dff48e69ca698` |
| [`morphogenesis/experiments/L1_field/x67_pattern_s174.json`](../morphogenesis/experiments/L1_field/x67_pattern_s174.json) | other | 16820 | `cf5d3b09c20aaddf759b8503da6b78296966f84619f54f6f465432baf792574d` |
| [`morphogenesis/experiments/L1_field/x67_pattern_s175.json`](../morphogenesis/experiments/L1_field/x67_pattern_s175.json) | other | 18737 | `e5a49eb9df3eb4c19199482ab3c483738ff82e58c6687ce1792d73a1e24130e6` |
| [`morphogenesis/experiments/L1_field/x67_series_index.json`](../morphogenesis/experiments/L1_field/x67_series_index.json) | other | 1049 | `63b9caeb75d03aa0bccb14642aba243d06bbffcd67550060e51bf3ea0a12a340` |
| [`morphogenesis/experiments/L1_field/x68_ov03_homog_s171.json`](../morphogenesis/experiments/L1_field/x68_ov03_homog_s171.json) | other | 9053 | `e117fdb9674656e1b4cad4cd1bb7766844bd9f0607c425c2d6eeda864f562ede` |
| [`morphogenesis/experiments/L1_field/x68_ov03_homog_s172.json`](../morphogenesis/experiments/L1_field/x68_ov03_homog_s172.json) | other | 9047 | `8be53e13e510180a16004a64094a120ae2073e51fede64ad4f4d4b06403cec65` |
| [`morphogenesis/experiments/L1_field/x68_ov03_homog_s173.json`](../morphogenesis/experiments/L1_field/x68_ov03_homog_s173.json) | other | 9054 | `186a1e22934cd337e689e0370d9fc3203dbc8099c536e19b4ff8dbf94232663f` |
| [`morphogenesis/experiments/L1_field/x68_ov03_homog_s174.json`](../morphogenesis/experiments/L1_field/x68_ov03_homog_s174.json) | other | 9052 | `89692658f91ecd564c4f301cd2860267f8d7715435dab174634de72ee59046fb` |
| [`morphogenesis/experiments/L1_field/x68_ov03_homog_s175.json`](../morphogenesis/experiments/L1_field/x68_ov03_homog_s175.json) | other | 9051 | `146131cb3957dc7161e2a071cb7a251e895e774404ed348700b57dd0e6ca07eb` |
| [`morphogenesis/experiments/L1_field/x68_ov03_pattern_s171.json`](../morphogenesis/experiments/L1_field/x68_ov03_pattern_s171.json) | other | 35497 | `251691416cac034c5eb5d494b1ee530ea515db158abfd333b84f725edb205342` |
| [`morphogenesis/experiments/L1_field/x68_ov03_pattern_s172.json`](../morphogenesis/experiments/L1_field/x68_ov03_pattern_s172.json) | other | 35499 | `20d1d47d3d12c86c69bbab4b8f2c969c16f9957c62aa5a1f3dc29e31aef011b3` |
| [`morphogenesis/experiments/L1_field/x68_ov03_pattern_s173.json`](../morphogenesis/experiments/L1_field/x68_ov03_pattern_s173.json) | other | 35505 | `6511c32d58ccb055ccbe5193fa960a71f17a7e47c5dfe60c279d042b28f68575` |
| [`morphogenesis/experiments/L1_field/x68_ov03_pattern_s174.json`](../morphogenesis/experiments/L1_field/x68_ov03_pattern_s174.json) | other | 35511 | `40d5be167c95c6359c43176ce3afc0f85f591d1685473ef44914f32ba64c33c8` |
| [`morphogenesis/experiments/L1_field/x68_ov03_pattern_s175.json`](../morphogenesis/experiments/L1_field/x68_ov03_pattern_s175.json) | other | 35486 | `b5cfcee0476d742be1666c1d1ac2a0b06ab51944b8ddee473813c1f181443aac` |
| [`morphogenesis/experiments/L1_field/x68_ov05_homog_s171.json`](../morphogenesis/experiments/L1_field/x68_ov05_homog_s171.json) | other | 9471 | `d081e39ea00dff545f61b41a4ce4360c72799bad7324a02d98356635586b63c8` |
| [`morphogenesis/experiments/L1_field/x68_ov05_homog_s172.json`](../morphogenesis/experiments/L1_field/x68_ov05_homog_s172.json) | other | 9461 | `baaa9d36543f354253b56c64da83927c44e4c41617f8bf547a3483ec55b0e3c3` |
| [`morphogenesis/experiments/L1_field/x68_ov05_homog_s173.json`](../morphogenesis/experiments/L1_field/x68_ov05_homog_s173.json) | other | 9471 | `a48992d388ea8555d9951c8b96d66df0ad42266ff92237dbdf8ad405aea8ec82` |
| [`morphogenesis/experiments/L1_field/x68_ov05_homog_s174.json`](../morphogenesis/experiments/L1_field/x68_ov05_homog_s174.json) | other | 9471 | `752559070b060863a78ea19ec17aa0011be564cfc713dd1feb719bbc885dd846` |
| [`morphogenesis/experiments/L1_field/x68_ov05_homog_s175.json`](../morphogenesis/experiments/L1_field/x68_ov05_homog_s175.json) | other | 9469 | `4fc891be7ea8ed3de076009fc125f5dcdd31f658673bda8bf874625f0ac25f00` |
| [`morphogenesis/experiments/L1_field/x68_ov05_pattern_s171.json`](../morphogenesis/experiments/L1_field/x68_ov05_pattern_s171.json) | other | 36336 | `59003b1f272a1f5dd271cbecfe4105c014a3561c99818d323a74650347452777` |
| [`morphogenesis/experiments/L1_field/x68_ov05_pattern_s172.json`](../morphogenesis/experiments/L1_field/x68_ov05_pattern_s172.json) | other | 36334 | `dd51fd8bec9b85574dd730a966548c3627b9b6cb84ae571630a7fc72de90921d` |
| [`morphogenesis/experiments/L1_field/x68_ov05_pattern_s173.json`](../morphogenesis/experiments/L1_field/x68_ov05_pattern_s173.json) | other | 36313 | `a52e37f71ec7427466b88c6e3957cec61581a381fca9f8ba2eea021a15ef1b75` |
| [`morphogenesis/experiments/L1_field/x68_ov05_pattern_s174.json`](../morphogenesis/experiments/L1_field/x68_ov05_pattern_s174.json) | other | 36341 | `29daf75d3d5e89b2f252dc2442f772e328c115718be525ca3f8d673804cb9838` |
| [`morphogenesis/experiments/L1_field/x68_ov05_pattern_s175.json`](../morphogenesis/experiments/L1_field/x68_ov05_pattern_s175.json) | other | 36325 | `fbd54d959b8e0ce643c893922163eb94238ffad4373c11a6b01ce01ec5fad441` |
| [`morphogenesis/experiments/L1_field/x68_ov07_homog_s171.json`](../morphogenesis/experiments/L1_field/x68_ov07_homog_s171.json) | other | 9471 | `89c7ee10a6a28f0c611671c71f65f048475c051e84553213dc14c84d1a866b79` |
| [`morphogenesis/experiments/L1_field/x68_ov07_homog_s172.json`](../morphogenesis/experiments/L1_field/x68_ov07_homog_s172.json) | other | 9461 | `53f9e03c76855322798c631788c912bdb992e357b31b5982f50bd655168a117a` |
| [`morphogenesis/experiments/L1_field/x68_ov07_homog_s173.json`](../morphogenesis/experiments/L1_field/x68_ov07_homog_s173.json) | other | 9471 | `07a892603dfa82e0ec09905853c9319ecc3d359b1e849849510f085e4c9ef68d` |
| [`morphogenesis/experiments/L1_field/x68_ov07_homog_s174.json`](../morphogenesis/experiments/L1_field/x68_ov07_homog_s174.json) | other | 9471 | `a9a24615bb4fb5811df8f5100d31ad7664208b6d299561e7ca9c9846db8aa289` |
| [`morphogenesis/experiments/L1_field/x68_ov07_homog_s175.json`](../morphogenesis/experiments/L1_field/x68_ov07_homog_s175.json) | other | 9469 | `187cb0ac982ce5d3c9abc24a037d045a353eb6c32b703208f0f2a48f25dca291` |
| [`morphogenesis/experiments/L1_field/x68_ov07_pattern_s171.json`](../morphogenesis/experiments/L1_field/x68_ov07_pattern_s171.json) | other | 42051 | `88e8452ecbf9a54a5493f33cd2a2aae1b9df17535d1bb81b1bda7b14b1bf61ab` |
| [`morphogenesis/experiments/L1_field/x68_ov07_pattern_s172.json`](../morphogenesis/experiments/L1_field/x68_ov07_pattern_s172.json) | other | 42067 | `a55544cad75832bb03cf4368a3713e24e5f9f63d7fb845278c0b91f94f02a9d7` |
| [`morphogenesis/experiments/L1_field/x68_ov07_pattern_s173.json`](../morphogenesis/experiments/L1_field/x68_ov07_pattern_s173.json) | other | 42044 | `c7975c0e53787fdd37c1bb96b35c136090f7864ced98ea59544db2d06741a912` |
| [`morphogenesis/experiments/L1_field/x68_ov07_pattern_s174.json`](../morphogenesis/experiments/L1_field/x68_ov07_pattern_s174.json) | other | 42048 | `c17534a5b53255d00299c005b415ea6e8790a7f614aae310c685a763d1090594` |
| [`morphogenesis/experiments/L1_field/x68_ov07_pattern_s175.json`](../morphogenesis/experiments/L1_field/x68_ov07_pattern_s175.json) | other | 42034 | `92edc35486594a7e9f9f67b90aa67f9ce1734243f6da26982efd28e53177b360` |
| [`morphogenesis/experiments/L1_field/x68_series_index.json`](../morphogenesis/experiments/L1_field/x68_series_index.json) | other | 3679 | `cad025735f6c7fbba2f9472d8ed52d3394b0c6e13c7612bc6bad964121412339` |
| [`morphogenesis/experiments/L1_field/x68r_ov03_homog_s171.json`](../morphogenesis/experiments/L1_field/x68r_ov03_homog_s171.json) | other | 10988 | `bc7c9729f11f5aebfff2c8d992c9543c7597652b569ac7ff1ae136924ffeaf8b` |
| [`morphogenesis/experiments/L1_field/x68r_ov03_homog_s172.json`](../morphogenesis/experiments/L1_field/x68r_ov03_homog_s172.json) | other | 8821 | `f080b7c512263b8f42d8b20b64decb108e8320007bf8b992abefe029912980bc` |
| [`morphogenesis/experiments/L1_field/x68r_ov03_homog_s173.json`](../morphogenesis/experiments/L1_field/x68r_ov03_homog_s173.json) | other | 9843 | `4500c82598d1de6d27c1090a8d340056c0eba71e4d9c4865378f09be11a7100f` |
| [`morphogenesis/experiments/L1_field/x68r_ov03_homog_s174.json`](../morphogenesis/experiments/L1_field/x68r_ov03_homog_s174.json) | other | 8841 | `9ce0e4dfade3fb3b19acc344176eab4b18a210d7a0355406be6b2a00b81bc008` |
| [`morphogenesis/experiments/L1_field/x68r_ov03_homog_s175.json`](../morphogenesis/experiments/L1_field/x68r_ov03_homog_s175.json) | other | 11261 | `caa1c07343bad7c23d224b1bdeaa65cce680e77470446483e71882b9029371fd` |
| [`morphogenesis/experiments/L1_field/x68r_ov03_pattern_s171.json`](../morphogenesis/experiments/L1_field/x68r_ov03_pattern_s171.json) | other | 37873 | `390ce2c9f92a7a140c1c990349432c0e6e593168170457aec0567fa74afabfe1` |
| [`morphogenesis/experiments/L1_field/x68r_ov03_pattern_s172.json`](../morphogenesis/experiments/L1_field/x68r_ov03_pattern_s172.json) | other | 43012 | `6f20d71a4cbd827b5190fd8714a499fdefca1ff2438f1a7b91c59a494e9de6e0` |
| [`morphogenesis/experiments/L1_field/x68r_ov03_pattern_s173.json`](../morphogenesis/experiments/L1_field/x68r_ov03_pattern_s173.json) | other | 40486 | `2788efff7f8b9006f5184626f278eadcdf1609e109cb8bfe677d7406e23a06b2` |
| [`morphogenesis/experiments/L1_field/x68r_ov03_pattern_s174.json`](../morphogenesis/experiments/L1_field/x68r_ov03_pattern_s174.json) | other | 40798 | `e917eed568ebd7a011e773d37e902ce7ee4ddf9ed17edf87d806aedebc7b54f9` |
| [`morphogenesis/experiments/L1_field/x68r_ov03_pattern_s175.json`](../morphogenesis/experiments/L1_field/x68r_ov03_pattern_s175.json) | other | 38784 | `dc7d2991425204a62c6ffaceb870a765bf1ea98d6e94e260dbb03c4f88c80782` |
| [`morphogenesis/experiments/L1_field/x68r_ov05_homog_s171.json`](../morphogenesis/experiments/L1_field/x68r_ov05_homog_s171.json) | other | 10988 | `85f7e0bc9c7dc67771bb937084efa3a9c8a1ad940c1f13402c32eeecfa756de7` |
| [`morphogenesis/experiments/L1_field/x68r_ov05_homog_s172.json`](../morphogenesis/experiments/L1_field/x68r_ov05_homog_s172.json) | other | 8821 | `56ea251a0ac32ccf43793f5f145c135c1837c7903f7863a0d9b5b6aad94f2395` |
| [`morphogenesis/experiments/L1_field/x68r_ov05_homog_s173.json`](../morphogenesis/experiments/L1_field/x68r_ov05_homog_s173.json) | other | 10259 | `60300f2a02e194cab334c686c045bb1355e450945ab1df3ce044005b7566762b` |
| [`morphogenesis/experiments/L1_field/x68r_ov05_homog_s174.json`](../morphogenesis/experiments/L1_field/x68r_ov05_homog_s174.json) | other | 8841 | `6de9fbf99aca45cd458f801e104e2eda37a97ebe74d794f23d196bcb435f21df` |
| [`morphogenesis/experiments/L1_field/x68r_ov05_homog_s175.json`](../morphogenesis/experiments/L1_field/x68r_ov05_homog_s175.json) | other | 11539 | `3edd0e41adb8f9708f9d6e8bfd74c6cc5f84b585c59faefb32794b5c7d8894b3` |
| [`morphogenesis/experiments/L1_field/x68r_ov05_pattern_s171.json`](../morphogenesis/experiments/L1_field/x68r_ov05_pattern_s171.json) | other | 38685 | `d8a7998e507aa3079c8b9ce2df26294180d6a4c5d9a77350a7eff5bd9fd0db1a` |
| [`morphogenesis/experiments/L1_field/x68r_ov05_pattern_s172.json`](../morphogenesis/experiments/L1_field/x68r_ov05_pattern_s172.json) | other | 44097 | `ca51088d00e2f4ee828b45df0547ca8cf7f79cdd5f8c993a015e49dce96bf4de` |
| [`morphogenesis/experiments/L1_field/x68r_ov05_pattern_s173.json`](../morphogenesis/experiments/L1_field/x68r_ov05_pattern_s173.json) | other | 40624 | `90e5755e38779877fcd145caeb7dd35ac1c9abc2bda4242a63148bbee636d2fc` |
| [`morphogenesis/experiments/L1_field/x68r_ov05_pattern_s174.json`](../morphogenesis/experiments/L1_field/x68r_ov05_pattern_s174.json) | other | 42493 | `32aceaa1d6a3cfb1a04d49f6ab8199c11d136bbfc2576f94184670d59e3ad606` |
| [`morphogenesis/experiments/L1_field/x68r_ov05_pattern_s175.json`](../morphogenesis/experiments/L1_field/x68r_ov05_pattern_s175.json) | other | 38784 | `644f9479e9e193ca9da8e8caf139bf6f39d353d72908b962f162c4e54b2ed301` |
| [`morphogenesis/experiments/L1_field/x68r_ov07_homog_s171.json`](../morphogenesis/experiments/L1_field/x68r_ov07_homog_s171.json) | other | 11114 | `fe4398dd719b878d1aa0cf1701fb568a274921040c399c6241c33d25ca8a26ff` |
| [`morphogenesis/experiments/L1_field/x68r_ov07_homog_s172.json`](../morphogenesis/experiments/L1_field/x68r_ov07_homog_s172.json) | other | 8821 | `f58a300dcbc033b0c188aa01166705efa1122a0c33484bbfeb027f08c38be035` |
| [`morphogenesis/experiments/L1_field/x68r_ov07_homog_s173.json`](../morphogenesis/experiments/L1_field/x68r_ov07_homog_s173.json) | other | 10259 | `18171b12f3bf34df7e9b77055f85baca80b1b8e5893fc1645b700bf7f50eef0d` |
| [`morphogenesis/experiments/L1_field/x68r_ov07_homog_s174.json`](../morphogenesis/experiments/L1_field/x68r_ov07_homog_s174.json) | other | 8841 | `bfe09c851e7d1c3a88b1657b5c47b0e186290f8baf3d3cf1cbacc8560451facf` |
| [`morphogenesis/experiments/L1_field/x68r_ov07_homog_s175.json`](../morphogenesis/experiments/L1_field/x68r_ov07_homog_s175.json) | other | 11539 | `376af79317c5590b7bf7a07cd7ddb638b2b061e4e979387959666ce9e821e5ee` |
| [`morphogenesis/experiments/L1_field/x68r_ov07_pattern_s171.json`](../morphogenesis/experiments/L1_field/x68r_ov07_pattern_s171.json) | other | 42659 | `a399b14ff864a587dae378345c49112a8addc6a03b1b024684ef03857bb98666` |
| [`morphogenesis/experiments/L1_field/x68r_ov07_pattern_s172.json`](../morphogenesis/experiments/L1_field/x68r_ov07_pattern_s172.json) | other | 51318 | `e93e5c17544cd9715f42a5afebb81f65fe7c18e5c16b6af3ea9499bf9181f315` |
| [`morphogenesis/experiments/L1_field/x68r_ov07_pattern_s173.json`](../morphogenesis/experiments/L1_field/x68r_ov07_pattern_s173.json) | other | 47563 | `0539ecc215f1c5dda406ac27d000a362346b96e8ff25ea2ad9ac5811265a7db7` |
| [`morphogenesis/experiments/L1_field/x68r_ov07_pattern_s174.json`](../morphogenesis/experiments/L1_field/x68r_ov07_pattern_s174.json) | other | 48721 | `cdb7f6cba6d447a34bbdcf7e8746b69d6ab39e33d9e13f695cfd46e63a121f8f` |
| [`morphogenesis/experiments/L1_field/x68r_ov07_pattern_s175.json`](../morphogenesis/experiments/L1_field/x68r_ov07_pattern_s175.json) | other | 47857 | `60311b40f90fab911385f54ec217d399c792c52175552f0e962e7f207b743095` |
| [`morphogenesis/experiments/L1_field/x68r_series_index.json`](../morphogenesis/experiments/L1_field/x68r_series_index.json) | other | 3590 | `cc13c5585db01543b1055a7320bceb65d4b30e39b52505e31abb7650e735218e` |
| [`morphogenesis/experiments/L1_field/x70_homog_s171.json`](../morphogenesis/experiments/L1_field/x70_homog_s171.json) | other | 13659 | `c3ac412964d12c9b561cdd5564b8b94e7f1b4c81a0297286e42acca0622561be` |
| [`morphogenesis/experiments/L1_field/x70_homog_s172.json`](../morphogenesis/experiments/L1_field/x70_homog_s172.json) | other | 13644 | `269daddcb54f1d5975bc57b277edf5c613db261dfec4e0b5d4c602769998e697` |
| [`morphogenesis/experiments/L1_field/x70_homog_s173.json`](../morphogenesis/experiments/L1_field/x70_homog_s173.json) | other | 13660 | `d32efbc7997b35aac355f0f990d5a2449c5b7dadb94a3a0915b42f5c23aa9c15` |
| [`morphogenesis/experiments/L1_field/x70_homog_s174.json`](../morphogenesis/experiments/L1_field/x70_homog_s174.json) | other | 13659 | `394c470f1808bff239166ec241853cf8360e321105e494b0c2fdd5dbd87b68d7` |
| [`morphogenesis/experiments/L1_field/x70_homog_s175.json`](../morphogenesis/experiments/L1_field/x70_homog_s175.json) | other | 13657 | `6f39dacf8cc7a3271b400657f2528563a1b46b28df83613b0bb6553b54f13a11` |
| [`morphogenesis/experiments/L1_field/x70_pattern_s171.json`](../morphogenesis/experiments/L1_field/x70_pattern_s171.json) | other | 74377 | `1a6d2307e32d469053a55c4761ae2f52aa8762b8f0cf3ce89d2989b2c6d4c3f2` |
| [`morphogenesis/experiments/L1_field/x70_pattern_s172.json`](../morphogenesis/experiments/L1_field/x70_pattern_s172.json) | other | 74362 | `9293fecf0b88baea32f5bd0c8e57f8fa80c0ba10ef92df1ad2b87a0273195db2` |
| [`morphogenesis/experiments/L1_field/x70_pattern_s173.json`](../morphogenesis/experiments/L1_field/x70_pattern_s173.json) | other | 74345 | `8ffed36929bed08f8990e151945b59da9a3d7a465493f79d948b48eb3bb25d1c` |
| [`morphogenesis/experiments/L1_field/x70_pattern_s174.json`](../morphogenesis/experiments/L1_field/x70_pattern_s174.json) | other | 74370 | `f612346c28834652caf7382ec175c3934c8dc135241745c55d616c01af2e69bf` |
| [`morphogenesis/experiments/L1_field/x70_pattern_s175.json`](../morphogenesis/experiments/L1_field/x70_pattern_s175.json) | other | 74368 | `75ce3b2af01becec450042ec1677a688f26a71739990e7bd4095a6e4a1a8ab54` |
| [`morphogenesis/experiments/L1_field/x70_series_index.json`](../morphogenesis/experiments/L1_field/x70_series_index.json) | other | 1039 | `346b59a9c6c607dec264b01f6c3da0ab632ba6f1a6e865d3b8a50f898c5b3a4c` |
| [`morphogenesis/experiments/L1_field/x70d_homog_s171.json`](../morphogenesis/experiments/L1_field/x70d_homog_s171.json) | other | 102456 | `53016d6ab3f4184b364aebd20b0dab64185c7b9a7a4d52cf6aa4e9a9f77f7c7e` |
| [`morphogenesis/experiments/L1_field/x70d_homog_s172.json`](../morphogenesis/experiments/L1_field/x70d_homog_s172.json) | other | 102316 | `aaf0a10a92abe862ef25725ab5a9b205b6ab25104cc707d9c27a408d7bb240aa` |
| [`morphogenesis/experiments/L1_field/x70d_homog_s173.json`](../morphogenesis/experiments/L1_field/x70d_homog_s173.json) | other | 102463 | `f109c7777c02e3b840b8531c2db1ad5ea8a999eb41b71a08712593daf510396d` |
| [`morphogenesis/experiments/L1_field/x70d_homog_s174.json`](../morphogenesis/experiments/L1_field/x70d_homog_s174.json) | other | 102460 | `2290a2635692a62e69be4e6df20a8957b52d6a0edd4cd979ec4f3feabc5757b1` |
| [`morphogenesis/experiments/L1_field/x70d_homog_s175.json`](../morphogenesis/experiments/L1_field/x70d_homog_s175.json) | other | 102434 | `d36600cb56d46433045b9af8b097f53e5845dccd4bc4ee61a663f1beadd6ad3a` |
| [`morphogenesis/experiments/L1_field/x70d_pattern_s171.json`](../morphogenesis/experiments/L1_field/x70d_pattern_s171.json) | other | 632460 | `6e2cde012ac2e515b9f131ffb0ba369bf677ff1bf4b57351d83926df4ebf47f8` |
| [`morphogenesis/experiments/L1_field/x70d_pattern_s172.json`](../morphogenesis/experiments/L1_field/x70d_pattern_s172.json) | other | 632392 | `bf50efc7f6fbf3603613986e1f7ac8f0739e6c2d8c8c3a78a8a008dca109123a` |
| [`morphogenesis/experiments/L1_field/x70d_pattern_s173.json`](../morphogenesis/experiments/L1_field/x70d_pattern_s173.json) | other | 632078 | `713552a993c2f313072f6000bd5662a215e5c55f089469b7bb602a8c6ff0765b` |
| [`morphogenesis/experiments/L1_field/x70d_pattern_s174.json`](../morphogenesis/experiments/L1_field/x70d_pattern_s174.json) | other | 632475 | `a9975ea33869d346c152a4c9f05ebe35a4ca8ed5b0225680ed6f7253abae474f` |
| [`morphogenesis/experiments/L1_field/x70d_pattern_s175.json`](../morphogenesis/experiments/L1_field/x70d_pattern_s175.json) | other | 632316 | `13cae82aef1170a99da884b5fee9d52f69805b9cf04a5789a4cb5e8b6237df29` |
| [`morphogenesis/experiments/L1_field/x70d_series_index.json`](../morphogenesis/experiments/L1_field/x70d_series_index.json) | other | 239 | `1499e71a32c80031ee0c0f549bee5a21004827d4e3d81d7d292f8fcba4dc825f` |
| [`morphogenesis/experiments/L1_field/x70r_homog_s171.json`](../morphogenesis/experiments/L1_field/x70r_homog_s171.json) | other | 130056 | `4e80d19e3b4c4a7ccfc3c7e81a369ae0736fd0386ba8e297818877fed315d44e` |
| [`morphogenesis/experiments/L1_field/x70r_homog_s172.json`](../morphogenesis/experiments/L1_field/x70r_homog_s172.json) | other | 84451 | `3ca0b56b852e73c3f2e6bef6a027bb4596c6529f765fa4fd8f64b26e5ca25b4e` |
| [`morphogenesis/experiments/L1_field/x70r_homog_s173.json`](../morphogenesis/experiments/L1_field/x70r_homog_s173.json) | other | 102547 | `458c4f8a7c85480a9ad04a224bc0c04c54a3ae3a794441c9dfe00e7ca239e9ce` |
| [`morphogenesis/experiments/L1_field/x70r_homog_s174.json`](../morphogenesis/experiments/L1_field/x70r_homog_s174.json) | other | 84745 | `ce2b04a9dc467cad7386d14c339774e8e419df007afee05ef18c055bbd1c435b` |
| [`morphogenesis/experiments/L1_field/x70r_homog_s175.json`](../morphogenesis/experiments/L1_field/x70r_homog_s175.json) | other | 129602 | `38afacf7b8d32834c56cc559807ec74569f711d2bd156a21ecb4f356b883fe50` |
| [`morphogenesis/experiments/L1_field/x70r_pattern_s171.json`](../morphogenesis/experiments/L1_field/x70r_pattern_s171.json) | other | 544744 | `84af007a2fdd1541cd7e12cdea38fe95ed2adbb7718df1f9ce76a3a66ea0ddbe` |
| [`morphogenesis/experiments/L1_field/x70r_pattern_s172.json`](../morphogenesis/experiments/L1_field/x70r_pattern_s172.json) | other | 628538 | `869fdc8d639c86fee0761f0cf3fceb18f258045afee99ffb881c007daf7d0458` |
| [`morphogenesis/experiments/L1_field/x70r_pattern_s173.json`](../morphogenesis/experiments/L1_field/x70r_pattern_s173.json) | other | 603495 | `50880230c390d9e7d711fd67284a48b1b815a9766bef847b57a745a2690e257b` |
| [`morphogenesis/experiments/L1_field/x70r_pattern_s174.json`](../morphogenesis/experiments/L1_field/x70r_pattern_s174.json) | other | 598123 | `13ef06a2ea3650e8b5021a0c01fbd376cc19fd9dd0c7516c9ea13f8474faf26e` |
| [`morphogenesis/experiments/L1_field/x70r_pattern_s175.json`](../morphogenesis/experiments/L1_field/x70r_pattern_s175.json) | other | 545393 | `49e0ec5eb3563f7a4554dd809c45a210720789a8f7765e20ccbbe55d1af89e4e` |
| [`morphogenesis/experiments/L1_field/x70r_series_index.json`](../morphogenesis/experiments/L1_field/x70r_series_index.json) | other | 1042 | `c0df238a135474e7bb1da26779f94f591f8c1a176859de0a492188244f98a546` |
| [`morphogenesis/experiments/L1_field/x71_f025_homog_s171.json`](../morphogenesis/experiments/L1_field/x71_f025_homog_s171.json) | other | 40376 | `c6267d3dd83b1c2465b62aec1b1abb709d9c1cb2cdbc55665eb7d40b63d1c510` |
| [`morphogenesis/experiments/L1_field/x71_f025_homog_s172.json`](../morphogenesis/experiments/L1_field/x71_f025_homog_s172.json) | other | 38747 | `d682191e43f906ff835444347d72d8f9d20fab306db6d519da3ed8f7c5fb2fe4` |
| [`morphogenesis/experiments/L1_field/x71_f025_homog_s173.json`](../morphogenesis/experiments/L1_field/x71_f025_homog_s173.json) | other | 38376 | `119d26b0aad08cc201d511cf0de97df663ad86519c33c6c3df46f5be4383848d` |
| [`morphogenesis/experiments/L1_field/x71_f025_homog_s174.json`](../morphogenesis/experiments/L1_field/x71_f025_homog_s174.json) | other | 38746 | `4e1dd3461569abe5a9ed158ea33d962ecf0198f5e194b3d8e8a19d321855495d` |
| [`morphogenesis/experiments/L1_field/x71_f025_homog_s175.json`](../morphogenesis/experiments/L1_field/x71_f025_homog_s175.json) | other | 40967 | `e05eaf055ccde9b665aa9a02631cd15e4f1093ff527a3770cbec9fbcc2c1fe5a` |
| [`morphogenesis/experiments/L1_field/x71_f025_pattern_s171.json`](../morphogenesis/experiments/L1_field/x71_f025_pattern_s171.json) | other | 46192 | `3bce8dc313b70c0e0e06b46b8e0e013922287ba7e73bf5e51f80c92b843305fe` |
| [`morphogenesis/experiments/L1_field/x71_f025_pattern_s172.json`](../morphogenesis/experiments/L1_field/x71_f025_pattern_s172.json) | other | 49727 | `c0b5639b700ac188385ac21793f6252514b89ca28a33579fecaacf5c35159b36` |
| [`morphogenesis/experiments/L1_field/x71_f025_pattern_s173.json`](../morphogenesis/experiments/L1_field/x71_f025_pattern_s173.json) | other | 52041 | `8bfc5d67ba9df52eff3d90dc59d9ae2bf43072b89b277fc77e38c925eed5ebfb` |
| [`morphogenesis/experiments/L1_field/x71_f025_pattern_s174.json`](../morphogenesis/experiments/L1_field/x71_f025_pattern_s174.json) | other | 50166 | `71726b44ed2286153ffae63c7aa5c029198c91d6542609aaef66dc283e24fe05` |
| [`morphogenesis/experiments/L1_field/x71_f025_pattern_s175.json`](../morphogenesis/experiments/L1_field/x71_f025_pattern_s175.json) | other | 55830 | `4d89d779a5b50b72ce70bccd98a26a1091ce7b9d6027c976b2f94cfd12b67a78` |
| [`morphogenesis/experiments/L1_field/x71_f030_homog_s171.json`](../morphogenesis/experiments/L1_field/x71_f030_homog_s171.json) | other | 28461 | `0cdf9d0cd1af5a0747f9ccfa29226e25fe4a9312a2c3add3008ec7f63b2531db` |
| [`morphogenesis/experiments/L1_field/x71_f030_homog_s172.json`](../morphogenesis/experiments/L1_field/x71_f030_homog_s172.json) | other | 25510 | `c86be5364faca049077e775a8ebf8d6e64d4bbf6b99a5e7893df0443656641fc` |
| [`morphogenesis/experiments/L1_field/x71_f030_homog_s173.json`](../morphogenesis/experiments/L1_field/x71_f030_homog_s173.json) | other | 36697 | `460c174ec86f745bd1e4ca22346cb4831a5e8fbeea6246930ac9cf2ad05eb5c2` |
| [`morphogenesis/experiments/L1_field/x71_f030_homog_s174.json`](../morphogenesis/experiments/L1_field/x71_f030_homog_s174.json) | other | 25517 | `2dc2625a8d074911dcb13463f2ac9ed843ebdffbde136318ff4ac04c137ba9f9` |
| [`morphogenesis/experiments/L1_field/x71_f030_homog_s175.json`](../morphogenesis/experiments/L1_field/x71_f030_homog_s175.json) | other | 37556 | `31df62b88ef8ac3ccacc4e5ed2ddc1a4426a5e15384ace31db7efd0c774e7d56` |
| [`morphogenesis/experiments/L1_field/x71_f030_pattern_s171.json`](../morphogenesis/experiments/L1_field/x71_f030_pattern_s171.json) | other | 61401 | `45840a1adc66cdc79b0102a1ae288b2d0327a7ed70e6a65b454974bdb0bbba62` |
| [`morphogenesis/experiments/L1_field/x71_f030_pattern_s172.json`](../morphogenesis/experiments/L1_field/x71_f030_pattern_s172.json) | other | 61045 | `9302785bff4bad77706e169347f9a3b24020b6f3ba570f4500e326850c57b0da` |
| [`morphogenesis/experiments/L1_field/x71_f030_pattern_s173.json`](../morphogenesis/experiments/L1_field/x71_f030_pattern_s173.json) | other | 59232 | `c6a4d240b380b8a24594b7c736e244b797369315d95eb675adb8064abccb6681` |
| [`morphogenesis/experiments/L1_field/x71_f030_pattern_s174.json`](../morphogenesis/experiments/L1_field/x71_f030_pattern_s174.json) | other | 54712 | `df8fc78addc07821fca40751776dddf30a6efcaf5e3e983e8b7e776d301bf0e2` |
| [`morphogenesis/experiments/L1_field/x71_f030_pattern_s175.json`](../morphogenesis/experiments/L1_field/x71_f030_pattern_s175.json) | other | 63501 | `2fc4aeb4fe29b9058bb76f6cb347c87d96dbb556abf574107d3c9cf1edf53518` |
| [`morphogenesis/experiments/L1_field/x71_f035_homog_s171.json`](../morphogenesis/experiments/L1_field/x71_f035_homog_s171.json) | other | 11231 | `f9c39eced4bcef1c37990c3cb9ebefe038b9a68154205130626f6d9a8e910fde` |
| [`morphogenesis/experiments/L1_field/x71_f035_homog_s172.json`](../morphogenesis/experiments/L1_field/x71_f035_homog_s172.json) | other | 9064 | `041cb0b29eacde76362926500ac2b7eb30c7990fa72e78291da2e8c24555d65b` |
| [`morphogenesis/experiments/L1_field/x71_f035_homog_s173.json`](../morphogenesis/experiments/L1_field/x71_f035_homog_s173.json) | other | 10502 | `0efca7827500d36e4d4ccd55528b0bf980962968f7bfb1dbdeb2c266ffc6ab78` |
| [`morphogenesis/experiments/L1_field/x71_f035_homog_s174.json`](../morphogenesis/experiments/L1_field/x71_f035_homog_s174.json) | other | 9084 | `c714bc2ea2f29acb0d10aef01263d3ba5911cf17d4b30f9d8e10a96e6f55723d` |
| [`morphogenesis/experiments/L1_field/x71_f035_homog_s175.json`](../morphogenesis/experiments/L1_field/x71_f035_homog_s175.json) | other | 11782 | `ce8b3af822efe3f1031df43ccedd829fb67c62ae8aa7be26857616da6685eedb` |
| [`morphogenesis/experiments/L1_field/x71_f035_pattern_s171.json`](../morphogenesis/experiments/L1_field/x71_f035_pattern_s171.json) | other | 38930 | `a9e8a7266b3c182d2ab32ad966819c4bd379eff68ee90cb24d2a46cafbf896d4` |
| [`morphogenesis/experiments/L1_field/x71_f035_pattern_s172.json`](../morphogenesis/experiments/L1_field/x71_f035_pattern_s172.json) | other | 44342 | `2ba82125fb597321e2cc583ce2f2770ed45bb0720f9e381dc033c659a4084e68` |
| [`morphogenesis/experiments/L1_field/x71_f035_pattern_s173.json`](../morphogenesis/experiments/L1_field/x71_f035_pattern_s173.json) | other | 40869 | `90a31efba56e264378771be24952b1403aa6ffb550876a32505198d6b0f9ca74` |
| [`morphogenesis/experiments/L1_field/x71_f035_pattern_s174.json`](../morphogenesis/experiments/L1_field/x71_f035_pattern_s174.json) | other | 42738 | `b04182ebb184922c6ab0e40c36cd47454646d4ecf9dfb306a8f11de49f632671` |
| [`morphogenesis/experiments/L1_field/x71_f035_pattern_s175.json`](../morphogenesis/experiments/L1_field/x71_f035_pattern_s175.json) | other | 39029 | `2839eaa3079e69ff804e1c26c78650d25d675d517197f9bc574418f586a2e873` |
| [`morphogenesis/experiments/L1_field/x71_f040_homog_s171.json`](../morphogenesis/experiments/L1_field/x71_f040_homog_s171.json) | other | 7386 | `19bb03e0b064db29b33b61aa71cf58355ce5697df3ae23158ccc544d3c481fc7` |
| [`morphogenesis/experiments/L1_field/x71_f040_homog_s172.json`](../morphogenesis/experiments/L1_field/x71_f040_homog_s172.json) | other | 8119 | `4b6f6a2692a971ab50fcade8b26c570780ca7cd9e9da47821adc5aac80012cb9` |
| [`morphogenesis/experiments/L1_field/x71_f040_homog_s173.json`](../morphogenesis/experiments/L1_field/x71_f040_homog_s173.json) | other | 8194 | `b3875ef859fd40d3a647216415c263fd3c5f697fc713499c1c8d90752f414da5` |
| [`morphogenesis/experiments/L1_field/x71_f040_homog_s174.json`](../morphogenesis/experiments/L1_field/x71_f040_homog_s174.json) | other | 8114 | `881e5b32513b42e68642ced35870ce12084e051f8417e8475ceb0508dc03712e` |
| [`morphogenesis/experiments/L1_field/x71_f040_homog_s175.json`](../morphogenesis/experiments/L1_field/x71_f040_homog_s175.json) | other | 8161 | `ba389c8a0c6953a2658aa0d708616111308bf092c8a6553a320bc26e1acdec0e` |
| [`morphogenesis/experiments/L1_field/x71_f040_pattern_s171.json`](../morphogenesis/experiments/L1_field/x71_f040_pattern_s171.json) | other | 21224 | `3373bdbaf32088cb331f1acd6a19c53e77bf519f2e74090b175d54f55b56f92c` |
| [`morphogenesis/experiments/L1_field/x71_f040_pattern_s172.json`](../morphogenesis/experiments/L1_field/x71_f040_pattern_s172.json) | other | 18348 | `738111e0693a8a11a809cf6e862d55daaa0c656d9371ebb372768166f4a324d8` |
| [`morphogenesis/experiments/L1_field/x71_f040_pattern_s173.json`](../morphogenesis/experiments/L1_field/x71_f040_pattern_s173.json) | other | 18878 | `12a23234c6d17c19f16ee82ee932d274d447b3de99b6af9d5181008831dcc546` |
| [`morphogenesis/experiments/L1_field/x71_f040_pattern_s174.json`](../morphogenesis/experiments/L1_field/x71_f040_pattern_s174.json) | other | 25193 | `1f310a1b537b642298f8b14121e9df4c9f4c353e52af3735211a7db2104c3c45` |
| [`morphogenesis/experiments/L1_field/x71_f040_pattern_s175.json`](../morphogenesis/experiments/L1_field/x71_f040_pattern_s175.json) | other | 19128 | `65c79778070e1365e88a6eb916cae8f6c01d4f975f8a479bba66d4f7b1b17adb` |
| [`morphogenesis/experiments/L1_field/x71_f045_homog_s171.json`](../morphogenesis/experiments/L1_field/x71_f045_homog_s171.json) | other | 8554 | `42ad4364adf172d5f948467213bed502a3e12f17502aaf81e93e46497fdb6c74` |
| [`morphogenesis/experiments/L1_field/x71_f045_homog_s172.json`](../morphogenesis/experiments/L1_field/x71_f045_homog_s172.json) | other | 9325 | `023734d2e34fc6ed43e19e3d63b357722b91f06996ef400dc86c3a5a3815aacb` |
| [`morphogenesis/experiments/L1_field/x71_f045_homog_s173.json`](../morphogenesis/experiments/L1_field/x71_f045_homog_s173.json) | other | 9703 | `48a46e20eb50dc7a9aabce01ba4649827d57f22f7cd22db2bfde469b861180f5` |
| [`morphogenesis/experiments/L1_field/x71_f045_homog_s174.json`](../morphogenesis/experiments/L1_field/x71_f045_homog_s174.json) | other | 9328 | `dd19f2aab71b955d6bb9ce684e88d85b0fa6a090cafe7fc016dcae26314135d1` |
| [`morphogenesis/experiments/L1_field/x71_f045_homog_s175.json`](../morphogenesis/experiments/L1_field/x71_f045_homog_s175.json) | other | 9124 | `a88550ee072d423886aa3b5cb75904fcde4ce9bb5dff6f656f79938fa8c69c19` |
| [`morphogenesis/experiments/L1_field/x71_f045_pattern_s171.json`](../morphogenesis/experiments/L1_field/x71_f045_pattern_s171.json) | other | 8871 | `5e40f3f95ea2c9545572e1cf192929f9d9376c9e17f9a2ac504cae65ba1c7bd7` |
| [`morphogenesis/experiments/L1_field/x71_f045_pattern_s172.json`](../morphogenesis/experiments/L1_field/x71_f045_pattern_s172.json) | other | 8638 | `a3a44f420823a83d776b1a30d5be847b4e57ed5d7d2d495ea479aefde09e16ab` |
| [`morphogenesis/experiments/L1_field/x71_f045_pattern_s173.json`](../morphogenesis/experiments/L1_field/x71_f045_pattern_s173.json) | other | 8021 | `a55d7592e6e37869d9a64a7fe29e67d88ec70921053b22fe80ca2a79f42f77f8` |
| [`morphogenesis/experiments/L1_field/x71_f045_pattern_s174.json`](../morphogenesis/experiments/L1_field/x71_f045_pattern_s174.json) | other | 8644 | `68daeaf4336382db7b477f3592dbcddc7ada333e4ba3b713ddbdc730c8aadc14` |
| [`morphogenesis/experiments/L1_field/x71_f045_pattern_s175.json`](../morphogenesis/experiments/L1_field/x71_f045_pattern_s175.json) | other | 8184 | `b073a592d4dc8cac4e6d9fba6b697ec4df39db528915c7c65f93692a10f02134` |
| [`morphogenesis/experiments/L1_field/x71_f050_homog_s171.json`](../morphogenesis/experiments/L1_field/x71_f050_homog_s171.json) | other | 7080 | `95baf7348dd196dfb534775b9f19e5857159c867159acff5dedfc62a30145c71` |
| [`morphogenesis/experiments/L1_field/x71_f050_homog_s172.json`](../morphogenesis/experiments/L1_field/x71_f050_homog_s172.json) | other | 7079 | `ca919eae5858f5f203b3e6969a4a4e4034a869b4bedd77c302b438f47c4f7c5f` |
| [`morphogenesis/experiments/L1_field/x71_f050_homog_s173.json`](../morphogenesis/experiments/L1_field/x71_f050_homog_s173.json) | other | 7082 | `c4b4207a111b12a329cd800702d060ac3f76f7bc70490663c168e35e2f812d19` |
| [`morphogenesis/experiments/L1_field/x71_f050_homog_s174.json`](../morphogenesis/experiments/L1_field/x71_f050_homog_s174.json) | other | 7079 | `cd140e8e044d18ff40a1088e492bb624aae894ca38f3eae3d26a0332fa266b61` |
| [`morphogenesis/experiments/L1_field/x71_f050_homog_s175.json`](../morphogenesis/experiments/L1_field/x71_f050_homog_s175.json) | other | 7078 | `804ce797d305c640226523fc0121c75bac803e4199dbc5c2b54a6bee45954048` |
| [`morphogenesis/experiments/L1_field/x71_f050_pattern_s171.json`](../morphogenesis/experiments/L1_field/x71_f050_pattern_s171.json) | other | 7136 | `d508c3d6df2848e3f90b9493c4030271b4ed3be8b80a61c547d7547b05a1a2d8` |
| [`morphogenesis/experiments/L1_field/x71_f050_pattern_s172.json`](../morphogenesis/experiments/L1_field/x71_f050_pattern_s172.json) | other | 7133 | `2a7e6be4e40e51d7bdf82cb713194a2ce30e5d054466255d6111903c2a26ac6e` |
| [`morphogenesis/experiments/L1_field/x71_f050_pattern_s173.json`](../morphogenesis/experiments/L1_field/x71_f050_pattern_s173.json) | other | 7135 | `26549874326140586728cad74d42c91f742221dfdaf339f3115787c140f0dde3` |
| [`morphogenesis/experiments/L1_field/x71_f050_pattern_s174.json`](../morphogenesis/experiments/L1_field/x71_f050_pattern_s174.json) | other | 7202 | `475256b3840803d4565e4473fa2d0eed775066094e7b024b69464c2238131e3b` |
| [`morphogenesis/experiments/L1_field/x71_f050_pattern_s175.json`](../morphogenesis/experiments/L1_field/x71_f050_pattern_s175.json) | other | 7201 | `a881873bd4174248090660b0edac5f3589c3e258d1b27895e468d38d039f0f4d` |
| [`morphogenesis/experiments/L1_field/x71_f055_homog_s171.json`](../morphogenesis/experiments/L1_field/x71_f055_homog_s171.json) | other | 7068 | `dbb69b5c7da0953bfd192972e3c06070b2601d0419fd50e6ba1f912c1e434679` |
| [`morphogenesis/experiments/L1_field/x71_f055_homog_s172.json`](../morphogenesis/experiments/L1_field/x71_f055_homog_s172.json) | other | 7067 | `3ab7c7844f6fb795f10d575137e9e6c358f3ff13d1498d9fb5ae3ef21b6306cc` |
| [`morphogenesis/experiments/L1_field/x71_f055_homog_s173.json`](../morphogenesis/experiments/L1_field/x71_f055_homog_s173.json) | other | 7066 | `1156885b4ccfdf455f17da291dc3562a6635366669658c155c3135d40c47ff0e` |
| [`morphogenesis/experiments/L1_field/x71_f055_homog_s174.json`](../morphogenesis/experiments/L1_field/x71_f055_homog_s174.json) | other | 7067 | `1b75ed66f337af852a84504ca8e4d0171955390fe99d0db74ee4b1c2ba1527fc` |
| [`morphogenesis/experiments/L1_field/x71_f055_homog_s175.json`](../morphogenesis/experiments/L1_field/x71_f055_homog_s175.json) | other | 7066 | `b11620af9634af2a113fc973f59c2112e85be94ceb4808599c1470ce7edf0c35` |
| [`morphogenesis/experiments/L1_field/x71_f055_pattern_s171.json`](../morphogenesis/experiments/L1_field/x71_f055_pattern_s171.json) | other | 7136 | `06e1191f2ff9ac32fc2467c5278c5bbe4ff460a0a14d288a4bec2d0194b96187` |
| [`morphogenesis/experiments/L1_field/x71_f055_pattern_s172.json`](../morphogenesis/experiments/L1_field/x71_f055_pattern_s172.json) | other | 7135 | `2e6fa038e1df3cfba9851ab6819e9260c2c3a8867df3966f5854120664e234b5` |
| [`morphogenesis/experiments/L1_field/x71_f055_pattern_s173.json`](../morphogenesis/experiments/L1_field/x71_f055_pattern_s173.json) | other | 7136 | `fb82e1d47c9d957fc17c404e5ff73d0898a1272e4b07079fd8b0137f4ec12ed0` |
| [`morphogenesis/experiments/L1_field/x71_f055_pattern_s174.json`](../morphogenesis/experiments/L1_field/x71_f055_pattern_s174.json) | other | 7133 | `d24d2a26739c724a262c31ae440338b178bb9b43920307442c6867e4bdbc73f1` |
| [`morphogenesis/experiments/L1_field/x71_f055_pattern_s175.json`](../morphogenesis/experiments/L1_field/x71_f055_pattern_s175.json) | other | 7136 | `5ff132af0bfcbfb838091034c94dd55e1ad380a3b7b522e23cf3fc7f4aa94713` |
| [`morphogenesis/experiments/L1_field/x71_series_index.json`](../morphogenesis/experiments/L1_field/x71_series_index.json) | other | 8434 | `d698c38efe74b6871be13e74afcf4f4192b67b0c934e18e3bf62cb1db6ce0c01` |
| [`morphogenesis/experiments/L1_field/x71b_pattern_s171.json`](../morphogenesis/experiments/L1_field/x71b_pattern_s171.json) | other | 151595 | `bac3e147412e3d71fe7f8499d0c6dab1501dd75221a18f498b190327a9ea5ec7` |
| [`morphogenesis/experiments/L1_field/x71b_pattern_s172.json`](../morphogenesis/experiments/L1_field/x71b_pattern_s172.json) | other | 162125 | `8753603b72a927504754d8420ca8b96cfa4029083856a16fe310e33d97a7af99` |
| [`morphogenesis/experiments/L1_field/x71b_pattern_s173.json`](../morphogenesis/experiments/L1_field/x71b_pattern_s173.json) | other | 158231 | `83f8d18f0473f3822ba33d66f81d9b75a0d19bd3bc2587d524f36692e4fc47a7` |
| [`morphogenesis/experiments/L1_field/x71b_pattern_s174.json`](../morphogenesis/experiments/L1_field/x71b_pattern_s174.json) | other | 168749 | `101991ce43eaa21464adf6468b7f089f414cc8b78a72e9c16380ff45a0311f51` |
| [`morphogenesis/experiments/L1_field/x71b_pattern_s175.json`](../morphogenesis/experiments/L1_field/x71b_pattern_s175.json) | other | 160319 | `5465ee28c3b7ef263f421d357ba1f245be01286e8328a8facaea920537a78aeb` |
| [`morphogenesis/experiments/L1_field/x71b_series_index.json`](../morphogenesis/experiments/L1_field/x71b_series_index.json) | other | 435 | `e8324fbddffabecb8b2c6ac21cfdf0d4ac871fe5fdd33319607c2f343674432f` |
| [`morphogenesis/experiments/L1_field/x71c_f033_pattern_s171.json`](../morphogenesis/experiments/L1_field/x71c_f033_pattern_s171.json) | other | 198133 | `5455b51d7f3fb0a500529deb49e680de3d9c636dccd4741f69114dd2e960b02f` |
| [`morphogenesis/experiments/L1_field/x71c_f033_pattern_s172.json`](../morphogenesis/experiments/L1_field/x71c_f033_pattern_s172.json) | other | 197822 | `822e92cea7870dc480e1a1a17069464ce0c8ccf09c44ebd38baebb641ec3740b` |
| [`morphogenesis/experiments/L1_field/x71c_f033_pattern_s173.json`](../morphogenesis/experiments/L1_field/x71c_f033_pattern_s173.json) | other | 209504 | `33405f5964b8c24524cc0c814d2da025faad851cd69e85a9482a78f929456f45` |
| [`morphogenesis/experiments/L1_field/x71c_f033_pattern_s174.json`](../morphogenesis/experiments/L1_field/x71c_f033_pattern_s174.json) | other | 253944 | `dfb627cd5d0424ae2a979b4a5c03c8f9e45ba39b0021a6aceceebbd86266517e` |
| [`morphogenesis/experiments/L1_field/x71c_f033_pattern_s175.json`](../morphogenesis/experiments/L1_field/x71c_f033_pattern_s175.json) | other | 221357 | `1608d979c2bc1867a59b64425734beca20cd87f60a0751d432539a407d3d1dbf` |
| [`morphogenesis/experiments/L1_field/x71c_f037_pattern_s171.json`](../morphogenesis/experiments/L1_field/x71c_f037_pattern_s171.json) | other | 108090 | `96b2a1daa869565d74a893526f57aa634747afbd3f9379039e9af834ff752e7a` |
| [`morphogenesis/experiments/L1_field/x71c_f037_pattern_s172.json`](../morphogenesis/experiments/L1_field/x71c_f037_pattern_s172.json) | other | 95397 | `349b945bdc369a05d8764d43c991903a5963c072168609ec2c1d5a6a7f4c5828` |
| [`morphogenesis/experiments/L1_field/x71c_f037_pattern_s173.json`](../morphogenesis/experiments/L1_field/x71c_f037_pattern_s173.json) | other | 108534 | `a30afd88feaedfc402a6c60372744e120b9480acb34c7308b818289e464934b6` |
| [`morphogenesis/experiments/L1_field/x71c_f037_pattern_s174.json`](../morphogenesis/experiments/L1_field/x71c_f037_pattern_s174.json) | other | 130947 | `9cacf58465d496be97c092209630e9cf0df322ce369ee5f3a04b42d3dd2d49e2` |
| [`morphogenesis/experiments/L1_field/x71c_f037_pattern_s175.json`](../morphogenesis/experiments/L1_field/x71c_f037_pattern_s175.json) | other | 99644 | `44b1b4a60eb125fe5095a3e7d2bdb699bc3d87e0ec08d5c3e59b5c391f05d13c` |
| [`morphogenesis/experiments/L1_field/x71c_series_index.json`](../morphogenesis/experiments/L1_field/x71c_series_index.json) | other | 1040 | `c41fc6eef63d19dd7ba9dc1e7b9a6a87c5799ee76d6145d0b6e07dbdbe2b7dea` |
| [`morphogenesis/experiments/L1_field/x72b_pattern_s171.json`](../morphogenesis/experiments/L1_field/x72b_pattern_s171.json) | other | 557672 | `46f18f7ac2d5f46814c126296afd994789b8bf1af6e5b1295111e39aed398385` |
| [`morphogenesis/experiments/L1_field/x72b_pattern_s172.json`](../morphogenesis/experiments/L1_field/x72b_pattern_s172.json) | other | 641466 | `140b5471595f603e9cda97ee08cc6da9ae1a2ccbb608033c041e101c4b1381bd` |
| [`morphogenesis/experiments/L1_field/x72b_pattern_s173.json`](../morphogenesis/experiments/L1_field/x72b_pattern_s173.json) | other | 616423 | `c5e7146acb647bea90cabea556d1f94d12a3ae3b169b4788835699bfd3d37599` |
| [`morphogenesis/experiments/L1_field/x72b_pattern_s174.json`](../morphogenesis/experiments/L1_field/x72b_pattern_s174.json) | other | 611051 | `bb3b415977e36325f82fa09e032c178fcfeb090eaa2b3935f9872c3e4605c0b9` |
| [`morphogenesis/experiments/L1_field/x72b_pattern_s175.json`](../morphogenesis/experiments/L1_field/x72b_pattern_s175.json) | other | 558321 | `62d4a8c5717fcb7e5e262c995aa6e2db93090d8c9dddffbc874a2fce36f047c2` |
| [`morphogenesis/experiments/L1_field/x72b_series_index.json`](../morphogenesis/experiments/L1_field/x72b_series_index.json) | other | 431 | `c4a6269b0f1f196f1dff6a95f2489d5b1fddb00ef6ae2af7d9d765b5f6d45734` |
| [`morphogenesis/experiments/L1_field/x72c_pattern_s171.json`](../morphogenesis/experiments/L1_field/x72c_pattern_s171.json) | other | 557672 | `73a728f1d8a2c4d295da91ca5df7eb77ef83a31a464422b5ad85aad9c2870c3f` |
| [`morphogenesis/experiments/L1_field/x72c_pattern_s172.json`](../morphogenesis/experiments/L1_field/x72c_pattern_s172.json) | other | 641466 | `0dcde3bab78487ba7bb5f930b774f6098d244d7f5e2eba8d2679a01f16c45aca` |
| [`morphogenesis/experiments/L1_field/x72c_pattern_s173.json`](../morphogenesis/experiments/L1_field/x72c_pattern_s173.json) | other | 616423 | `dc911b6fd828766dc04dee5ec7317743a5b194867e95bc4ca882b1c6306b5f36` |
| [`morphogenesis/experiments/L1_field/x72c_pattern_s174.json`](../morphogenesis/experiments/L1_field/x72c_pattern_s174.json) | other | 611051 | `b1ffec2a2d1451f930dfb3731f856f2e0762630b0e7f638980c3ed90ce2222b1` |
| [`morphogenesis/experiments/L1_field/x72c_pattern_s175.json`](../morphogenesis/experiments/L1_field/x72c_pattern_s175.json) | other | 558321 | `db533b26e1d31f33d6705e0d967718849742708845983b98184bb7b906fd605e` |
| [`morphogenesis/experiments/L1_field/x72c_pattern_s176.json`](../morphogenesis/experiments/L1_field/x72c_pattern_s176.json) | other | 534243 | `6dbcad6c67d88b6f187835461a53bbaae68f169e7c483901ab4a20579494b87c` |
| [`morphogenesis/experiments/L1_field/x72c_pattern_s177.json`](../morphogenesis/experiments/L1_field/x72c_pattern_s177.json) | other | 660443 | `1fa3d48816963bf55725e365181b9fcbcc9937f4a9e7d6d8b67d2d30aa36daa4` |
| [`morphogenesis/experiments/L1_field/x72c_pattern_s178.json`](../morphogenesis/experiments/L1_field/x72c_pattern_s178.json) | other | 601786 | `96efcef809079a1daa4b90e1fdfedb607485209a71755a24972ebd33ea49c342` |
| [`morphogenesis/experiments/L1_field/x72c_pattern_s179.json`](../morphogenesis/experiments/L1_field/x72c_pattern_s179.json) | other | 536173 | `164d9973b8f061d24a7626fbe34da5529bf5bf77441dba3dc3207b46d2394ab5` |
| [`morphogenesis/experiments/L1_field/x72c_pattern_s180.json`](../morphogenesis/experiments/L1_field/x72c_pattern_s180.json) | other | 597813 | `ff866b6109385902c243a1792f9cae14b59450bd8da4106b1f54e9a63812d46e` |
| [`morphogenesis/experiments/L1_field/x72c_series_index.json`](../morphogenesis/experiments/L1_field/x72c_series_index.json) | other | 810 | `1bb55e1066034e5ab41d5b039c8505ae7559023d1cd74ad7628835ab85a0281b` |
| [`morphogenesis/experiments/L1_field/x74_f030_pattern_s171.json`](../morphogenesis/experiments/L1_field/x74_f030_pattern_s171.json) | other | 969225 | `06f1bb4d7c6c30d681aab5d67f8dceb2db264ff2dd8a8d07f80ce4073113cffa` |
| [`morphogenesis/experiments/L1_field/x74_f030_pattern_s172.json`](../morphogenesis/experiments/L1_field/x74_f030_pattern_s172.json) | other | 926856 | `37174ac85ad3714213fd2a0cd0fa897f31ba009c75908baf6520768796dade57` |
| [`morphogenesis/experiments/L1_field/x74_f030_pattern_s173.json`](../morphogenesis/experiments/L1_field/x74_f030_pattern_s173.json) | other | 887753 | `d860417fc3ea8f5dba6d84e7b63126c7e5e1c518371876528e95cc2bf716ae2a` |
| [`morphogenesis/experiments/L1_field/x74_f030_pattern_s174.json`](../morphogenesis/experiments/L1_field/x74_f030_pattern_s174.json) | other | 867508 | `e47e925b6dd12902e1cc2765d38e6209aec0b2c17d6de71d2b0e9e78eef89b0f` |
| [`morphogenesis/experiments/L1_field/x74_f030_pattern_s175.json`](../morphogenesis/experiments/L1_field/x74_f030_pattern_s175.json) | other | 951493 | `863e6828a6e1e9c008a4a4dba3b4ab015116bf692366dfc599600ba68dec7534` |
| [`morphogenesis/experiments/L1_field/x74_f040_pattern_s171.json`](../morphogenesis/experiments/L1_field/x74_f040_pattern_s171.json) | other | 217645 | `b8cd8fbfc5d763e42404da0e5126a962f8ae641858078f97282226f616f4e2e1` |
| [`morphogenesis/experiments/L1_field/x74_f040_pattern_s172.json`](../morphogenesis/experiments/L1_field/x74_f040_pattern_s172.json) | other | 203591 | `4953f0f23e704e209ceb58c27d587168f91c36f5a607d677fd5f6d4d997addda` |
| [`morphogenesis/experiments/L1_field/x74_f040_pattern_s173.json`](../morphogenesis/experiments/L1_field/x74_f040_pattern_s173.json) | other | 184288 | `cad97c60cd2a705f05f46c2db69a90863817e8a86f22c54db453a901f5443cec` |
| [`morphogenesis/experiments/L1_field/x74_f040_pattern_s174.json`](../morphogenesis/experiments/L1_field/x74_f040_pattern_s174.json) | other | 253424 | `2b6f9d6cb4b7533c325639e773a7185cab3baf0617f87ad22fa647728c7f9821` |
| [`morphogenesis/experiments/L1_field/x74_f040_pattern_s175.json`](../morphogenesis/experiments/L1_field/x74_f040_pattern_s175.json) | other | 181985 | `efd70259dfb134ef4ffb44a4fa2693a795e410eb769a3f098e3337ad78c30041` |
| [`morphogenesis/experiments/L1_field/x74_series_index.json`](../morphogenesis/experiments/L1_field/x74_series_index.json) | other | 1034 | `8f3487db89624804e1b42ac569a07a0cdb97274e54124478eb84829291a35974` |
| [`morphogenesis/experiments/L1_field/x75_f033_pattern_s171.json`](../morphogenesis/experiments/L1_field/x75_f033_pattern_s171.json) | other | 747951 | `1a24d436cfab3e2a0258ff65181b5963cd060e638f66a72453e0d81638659605` |
| [`morphogenesis/experiments/L1_field/x75_f033_pattern_s172.json`](../morphogenesis/experiments/L1_field/x75_f033_pattern_s172.json) | other | 686351 | `da74e0bf57225ea2201e1eee9aa9450f7351f0c3e2b93aa54c1f6f9bc6ffd662` |
| [`morphogenesis/experiments/L1_field/x75_f033_pattern_s173.json`](../morphogenesis/experiments/L1_field/x75_f033_pattern_s173.json) | other | 733227 | `ee87bfe5e01af75c89b402d62bd43b6cd97519c15bd9b2bb51f9f9a7556b8e20` |
| [`morphogenesis/experiments/L1_field/x75_f033_pattern_s174.json`](../morphogenesis/experiments/L1_field/x75_f033_pattern_s174.json) | other | 919826 | `6e3462b4fa08500b6af84cd46253e6e7846cd2b6ad4255e44bf9e229fdc2c95b` |
| [`morphogenesis/experiments/L1_field/x75_f033_pattern_s175.json`](../morphogenesis/experiments/L1_field/x75_f033_pattern_s175.json) | other | 821744 | `5c756ac41efe21225ab22441555adfff0eaf3c5572876d4e3991fc8e156ec769` |
| [`morphogenesis/experiments/L1_field/x75_f037_pattern_s171.json`](../morphogenesis/experiments/L1_field/x75_f037_pattern_s171.json) | other | 408497 | `e27b7ce66e45dd53f33158dce95283e809fb3cac015b21490461887c51ea2ae3` |
| [`morphogenesis/experiments/L1_field/x75_f037_pattern_s172.json`](../morphogenesis/experiments/L1_field/x75_f037_pattern_s172.json) | other | 366244 | `ba00fc6a05cc877681612cfe3723b3a6aa9c244301985422d545b414d04dbbe4` |
| [`morphogenesis/experiments/L1_field/x75_f037_pattern_s173.json`](../morphogenesis/experiments/L1_field/x75_f037_pattern_s173.json) | other | 431620 | `2b9fd35657ff8ff07b19d6bd787975e17242fb06a3d1b2377905488ae74d2ad6` |
| [`morphogenesis/experiments/L1_field/x75_f037_pattern_s174.json`](../morphogenesis/experiments/L1_field/x75_f037_pattern_s174.json) | other | 425091 | `dbebf798ebde190f486c1c51ebbc7e338e971847f6c80998dd900dd37d980943` |
| [`morphogenesis/experiments/L1_field/x75_f037_pattern_s175.json`](../morphogenesis/experiments/L1_field/x75_f037_pattern_s175.json) | other | 393503 | `d308e85f7f2cdda51c99d1588482576a7271b5bff61b49b583df42464ad3c351` |
| [`morphogenesis/experiments/L1_field/x75_series_index.json`](../morphogenesis/experiments/L1_field/x75_series_index.json) | other | 1032 | `71fa19b1dc40791f130a4f6ca748fd6daedaed8973fddb66d2669d98fc2ebf5d` |
| [`morphogenesis/experiments/L1_field/x76_f033_pattern_s171.json`](../morphogenesis/experiments/L1_field/x76_f033_pattern_s171.json) | other | 747951 | `1a24d436cfab3e2a0258ff65181b5963cd060e638f66a72453e0d81638659605` |
| [`morphogenesis/experiments/L1_field/x76_f033_pattern_s172.json`](../morphogenesis/experiments/L1_field/x76_f033_pattern_s172.json) | other | 686351 | `da74e0bf57225ea2201e1eee9aa9450f7351f0c3e2b93aa54c1f6f9bc6ffd662` |
| [`morphogenesis/experiments/L1_field/x76_f033_pattern_s173.json`](../morphogenesis/experiments/L1_field/x76_f033_pattern_s173.json) | other | 733227 | `ee87bfe5e01af75c89b402d62bd43b6cd97519c15bd9b2bb51f9f9a7556b8e20` |
| [`morphogenesis/experiments/L1_field/x76_f033_pattern_s174.json`](../morphogenesis/experiments/L1_field/x76_f033_pattern_s174.json) | other | 919826 | `6e3462b4fa08500b6af84cd46253e6e7846cd2b6ad4255e44bf9e229fdc2c95b` |
| [`morphogenesis/experiments/L1_field/x76_f033_pattern_s175.json`](../morphogenesis/experiments/L1_field/x76_f033_pattern_s175.json) | other | 821744 | `5c756ac41efe21225ab22441555adfff0eaf3c5572876d4e3991fc8e156ec769` |
| [`morphogenesis/experiments/L1_field/x76_f033_pattern_s176.json`](../morphogenesis/experiments/L1_field/x76_f033_pattern_s176.json) | other | 731566 | `44e96ad53b620cf0e662a2ee4a8681d39704e47f6896fb91572b8b6cd6e19e39` |
| [`morphogenesis/experiments/L1_field/x76_f033_pattern_s177.json`](../morphogenesis/experiments/L1_field/x76_f033_pattern_s177.json) | other | 825619 | `00f1cee272c9932236b3b4a701ff55b51fa6f0208bb92e958010e61e5c8a07ea` |
| [`morphogenesis/experiments/L1_field/x76_f033_pattern_s178.json`](../morphogenesis/experiments/L1_field/x76_f033_pattern_s178.json) | other | 790860 | `ad2f848674a59407dc843b2351268ed8caea4e1111fb302e8914e1615dc40e33` |
| [`morphogenesis/experiments/L1_field/x76_f033_pattern_s179.json`](../morphogenesis/experiments/L1_field/x76_f033_pattern_s179.json) | other | 769623 | `a64a04bbadd93d1428d7953aaf518aaf301b26516feeca86329651bb9fc70d28` |
| [`morphogenesis/experiments/L1_field/x76_f033_pattern_s180.json`](../morphogenesis/experiments/L1_field/x76_f033_pattern_s180.json) | other | 877032 | `d3a70261b23df70612e35cc401fa32eac0f08242e73b42651ba5ae4f8345e623` |
| [`morphogenesis/experiments/L1_field/x76_series_index.json`](../morphogenesis/experiments/L1_field/x76_series_index.json) | other | 1036 | `8ac48f75a64e05fad5d6187c265a4cfe9095d83d062393bfda78cd4fdef36f35` |
| [`morphogenesis/experiments/L1_field/x78_match_s171.json`](../morphogenesis/experiments/L1_field/x78_match_s171.json) | other | 67831 | `eda52e670439b6726e199259cf827f618c46ede499243b73ec529c158a514bfb` |
| [`morphogenesis/experiments/L1_field/x78_match_s172.json`](../morphogenesis/experiments/L1_field/x78_match_s172.json) | other | 65333 | `34dd4be6566f61d64eb48254bcce9a352a9da9e76aa169c4d35078cc0b73f3b0` |
| [`morphogenesis/experiments/L1_field/x78_match_s173.json`](../morphogenesis/experiments/L1_field/x78_match_s173.json) | other | 68610 | `1227ef538f3e5fd832a664f0d6557649c0f36cc88d80829c52710753ad1700c6` |
| [`morphogenesis/experiments/L1_field/x78_match_s174.json`](../morphogenesis/experiments/L1_field/x78_match_s174.json) | other | 67360 | `bc4c2f324d2743dae4d574073b9792ce7690806b8be6d5ff608fb938e880e3a6` |
| [`morphogenesis/experiments/L1_field/x78_match_s175.json`](../morphogenesis/experiments/L1_field/x78_match_s175.json) | other | 67220 | `592baecf46e2756d1162b83e857bf922fc791eb78ccd1fc359c114b9704dd24b` |
| [`morphogenesis/experiments/L1_field/x78_match_s176.json`](../morphogenesis/experiments/L1_field/x78_match_s176.json) | other | 64667 | `c456d9d9356c2c5df7685323b92fcbe97b975268890946f5fc5dfb547b2e92fc` |
| [`morphogenesis/experiments/L1_field/x78_match_s177.json`](../morphogenesis/experiments/L1_field/x78_match_s177.json) | other | 65489 | `8cb38b736af3d8ee3184bee060078c340abfcf80ff8f2fe2cf280bbccbfec2c9` |
| [`morphogenesis/experiments/L1_field/x78_match_s178.json`](../morphogenesis/experiments/L1_field/x78_match_s178.json) | other | 66369 | `a5fe99a6c212d2517ba4cf8e7b4797810dafa7cb2135e62c3c3ebaa1ba66e067` |
| [`morphogenesis/experiments/L1_field/x78_match_s179.json`](../morphogenesis/experiments/L1_field/x78_match_s179.json) | other | 64767 | `1a1e6ac9aed555f052ad48b2ef39320fec6e4d95d3fe6e919f0a0075baafe8fe` |
| [`morphogenesis/experiments/L1_field/x78_match_s180.json`](../morphogenesis/experiments/L1_field/x78_match_s180.json) | other | 67240 | `3b4268e38bb8c6bf315e63f4bc52af9f710161db5c0c2d192f5704ee0b9ec8ce` |
| [`morphogenesis/experiments/L1_field/x78_mismatch_s171.json`](../morphogenesis/experiments/L1_field/x78_mismatch_s171.json) | other | 217645 | `b8cd8fbfc5d763e42404da0e5126a962f8ae641858078f97282226f616f4e2e1` |
| [`morphogenesis/experiments/L1_field/x78_mismatch_s172.json`](../morphogenesis/experiments/L1_field/x78_mismatch_s172.json) | other | 203591 | `4953f0f23e704e209ceb58c27d587168f91c36f5a607d677fd5f6d4d997addda` |
| [`morphogenesis/experiments/L1_field/x78_mismatch_s173.json`](../morphogenesis/experiments/L1_field/x78_mismatch_s173.json) | other | 184288 | `cad97c60cd2a705f05f46c2db69a90863817e8a86f22c54db453a901f5443cec` |
| [`morphogenesis/experiments/L1_field/x78_mismatch_s174.json`](../morphogenesis/experiments/L1_field/x78_mismatch_s174.json) | other | 253424 | `2b6f9d6cb4b7533c325639e773a7185cab3baf0617f87ad22fa647728c7f9821` |
| [`morphogenesis/experiments/L1_field/x78_mismatch_s175.json`](../morphogenesis/experiments/L1_field/x78_mismatch_s175.json) | other | 181985 | `efd70259dfb134ef4ffb44a4fa2693a795e410eb769a3f098e3337ad78c30041` |
| [`morphogenesis/experiments/L1_field/x78_mismatch_s176.json`](../morphogenesis/experiments/L1_field/x78_mismatch_s176.json) | other | 184903 | `77840dbf59a8eb33ee62489254e64daa13035b62263586e6fc3f15179b6a8fbe` |
| [`morphogenesis/experiments/L1_field/x78_mismatch_s177.json`](../morphogenesis/experiments/L1_field/x78_mismatch_s177.json) | other | 228910 | `28d47ab812cfec53d9732610a32368d69e3b62556701c4d498c34257872e7c61` |
| [`morphogenesis/experiments/L1_field/x78_mismatch_s178.json`](../morphogenesis/experiments/L1_field/x78_mismatch_s178.json) | other | 191000 | `0588faa7c39c11ebdfb4a995181d23406fb1b3f5d2d3f9e55a6eb601926c178b` |
| [`morphogenesis/experiments/L1_field/x78_mismatch_s179.json`](../morphogenesis/experiments/L1_field/x78_mismatch_s179.json) | other | 191839 | `2531c6deaa81507bb92abf1c504feb6b4a3036a6c435ce3a50784e1cf2d3f3aa` |
| [`morphogenesis/experiments/L1_field/x78_mismatch_s180.json`](../morphogenesis/experiments/L1_field/x78_mismatch_s180.json) | other | 201627 | `d91c194757000240fea373fca9ffb1544c4e3c2f5527e37ce4b769747d694c68` |
| [`morphogenesis/experiments/L1_field/x78_series_index.json`](../morphogenesis/experiments/L1_field/x78_series_index.json) | other | 2059 | `8ff67df70b6325bc56aa27c9c3c78fb241cc9902850ad979c44eb1520496cf1d` |
| [`morphogenesis/experiments/L1_field/x78b_series_index.json`](../morphogenesis/experiments/L1_field/x78b_series_index.json) | other | 1030 | `586a085aa6a5f99d6496b676bd0c5a20142b68da39e728a6fce4db6a93c25d1c` |
| [`morphogenesis/experiments/L1_field/x78b_two_scale_s171.json`](../morphogenesis/experiments/L1_field/x78b_two_scale_s171.json) | other | 613075 | `0e02ceb8c97efd2787cb14d5e6d5067fe44a24d82ea9b34543f9ea14e7462a26` |
| [`morphogenesis/experiments/L1_field/x78b_two_scale_s172.json`](../morphogenesis/experiments/L1_field/x78b_two_scale_s172.json) | other | 589574 | `b88bcb3e6817e9d54e0b80761b56b01cfc03140d80a3a5d678e216d59b0ab17a` |
| [`morphogenesis/experiments/L1_field/x78b_two_scale_s173.json`](../morphogenesis/experiments/L1_field/x78b_two_scale_s173.json) | other | 634692 | `d94547708818c0acc00c75ce6e6948b0ebfe542aff031da638251c59925a1ee1` |
| [`morphogenesis/experiments/L1_field/x78b_two_scale_s174.json`](../morphogenesis/experiments/L1_field/x78b_two_scale_s174.json) | other | 661535 | `f0902c0ed1664455a294f50e122ace7dfca4686238ff6332476a58ba891b0c9c` |
| [`morphogenesis/experiments/L1_field/x78b_two_scale_s175.json`](../morphogenesis/experiments/L1_field/x78b_two_scale_s175.json) | other | 525518 | `16f7cf18db122a0c7b63770254f8aa2fe438d7aa4ed07d65ded2fcad97a0e214` |
| [`morphogenesis/experiments/L1_field/x78b_two_scale_s176.json`](../morphogenesis/experiments/L1_field/x78b_two_scale_s176.json) | other | 596586 | `ca11f559e357321bde48973cbf576433cd3ea84716f4b98901ca15146a47d843` |
| [`morphogenesis/experiments/L1_field/x78b_two_scale_s177.json`](../morphogenesis/experiments/L1_field/x78b_two_scale_s177.json) | other | 649078 | `31ca7a7a7f9f26d498b47429d072187d2c3a07de3cc5bd752cfc6593bbbc194b` |
| [`morphogenesis/experiments/L1_field/x78b_two_scale_s178.json`](../morphogenesis/experiments/L1_field/x78b_two_scale_s178.json) | other | 637359 | `9007085e2b9cdba2eb906f6032fb1bc4a8ae327f1f2934e188396dbe05621030` |
| [`morphogenesis/experiments/L1_field/x78b_two_scale_s179.json`](../morphogenesis/experiments/L1_field/x78b_two_scale_s179.json) | other | 637685 | `9c37a531078b02a2e7cb90b0b984ed62b4d428e83dd94e1ec1dd0d7b9f233d4f` |
| [`morphogenesis/experiments/L1_field/x78b_two_scale_s180.json`](../morphogenesis/experiments/L1_field/x78b_two_scale_s180.json) | other | 535199 | `6dc2552fd498332da1ac39d2f0401e0ee8dbc6dab4d156250b60fb66190bb215` |
| [`morphogenesis/experiments/L1_field/x79_mix025_s171.json`](../morphogenesis/experiments/L1_field/x79_mix025_s171.json) | other | 763826 | `35c9d5b2f0104f1669b847f4cc6a5469380ff542b69d9bce4a00e7e79755fc92` |
| [`morphogenesis/experiments/L1_field/x79_mix025_s172.json`](../morphogenesis/experiments/L1_field/x79_mix025_s172.json) | other | 819375 | `f44e9d8760852f64b6d3bf0f535cfc4b74c29a95e65ecf4959b08f7d4ae7351d` |
| [`morphogenesis/experiments/L1_field/x79_mix025_s173.json`](../morphogenesis/experiments/L1_field/x79_mix025_s173.json) | other | 838334 | `2895d8a0833858ac3044397e171d53996ef6721d09b5644160f5f65b3ae38d97` |
| [`morphogenesis/experiments/L1_field/x79_mix025_s174.json`](../morphogenesis/experiments/L1_field/x79_mix025_s174.json) | other | 838423 | `523ad46f70d87da74ecb2de49e0e4f50e58e13c26c33f3784ac7bbdb31b625ae` |
| [`morphogenesis/experiments/L1_field/x79_mix025_s175.json`](../morphogenesis/experiments/L1_field/x79_mix025_s175.json) | other | 785473 | `95f06c6b3351edef889d4420d8839e0852574c3e50061c0a6e12617ca1e0e977` |
| [`morphogenesis/experiments/L1_field/x79_mix025_s176.json`](../morphogenesis/experiments/L1_field/x79_mix025_s176.json) | other | 801549 | `580c06ab3fef7d0de83bc692e0dc832c01f900e45bdfe20e666267545f969142` |
| [`morphogenesis/experiments/L1_field/x79_mix025_s177.json`](../morphogenesis/experiments/L1_field/x79_mix025_s177.json) | other | 789151 | `4abb9723e70195fbb8e97fd9e887770235f8ddb47ac4b735768fc7bae6696fb5` |
| [`morphogenesis/experiments/L1_field/x79_mix025_s178.json`](../morphogenesis/experiments/L1_field/x79_mix025_s178.json) | other | 737928 | `0bfe0c58baeb592315a8b7991b5de524aef97bddef6865607d7400fd18d5845f` |
| [`morphogenesis/experiments/L1_field/x79_mix025_s179.json`](../morphogenesis/experiments/L1_field/x79_mix025_s179.json) | other | 831260 | `0500c74330f7e14b4a2f45870df96b8b6022043e683182fccf93a317dc913d2e` |
| [`morphogenesis/experiments/L1_field/x79_mix025_s180.json`](../morphogenesis/experiments/L1_field/x79_mix025_s180.json) | other | 812932 | `27df303f629423a01e0ba6cd83c7fe8d1646c14dfd626a14658b0c69afc2209c` |
| [`morphogenesis/experiments/L1_field/x79_mix075_s171.json`](../morphogenesis/experiments/L1_field/x79_mix075_s171.json) | other | 510306 | `c518b6f482e416047e9f5bdbf7196d2694116b66b20f1678abb61b037b280416` |
| [`morphogenesis/experiments/L1_field/x79_mix075_s172.json`](../morphogenesis/experiments/L1_field/x79_mix075_s172.json) | other | 602981 | `f8196e62e37a88443d7475ab1b86e44c329118e427f6f3190a874a4dfbc0f2e8` |
| [`morphogenesis/experiments/L1_field/x79_mix075_s173.json`](../morphogenesis/experiments/L1_field/x79_mix075_s173.json) | other | 451904 | `9e827af3c86fc897831a7d207f1f4e6859c39916c85c49101c26346a218c29c9` |
| [`morphogenesis/experiments/L1_field/x79_mix075_s174.json`](../morphogenesis/experiments/L1_field/x79_mix075_s174.json) | other | 566173 | `45e697e911c1960ff8ca9d2e40d15b433ec45c72d21d5b7fcf3e6056eb38f1cf` |
| [`morphogenesis/experiments/L1_field/x79_mix075_s175.json`](../morphogenesis/experiments/L1_field/x79_mix075_s175.json) | other | 552846 | `649fabc3f7e1038af0709201fbbc579bd07d3bf455d527b421d7b8eaf83b886b` |
| [`morphogenesis/experiments/L1_field/x79_mix075_s176.json`](../morphogenesis/experiments/L1_field/x79_mix075_s176.json) | other | 460995 | `b53340d1f9c237e3bfd8a78efea36a9200b55d7042022e2453eb7c1f5e15d092` |
| [`morphogenesis/experiments/L1_field/x79_mix075_s177.json`](../morphogenesis/experiments/L1_field/x79_mix075_s177.json) | other | 566266 | `e8e87b8fe6b2f4477ead0d87d85536bd2bb898ebc6663063342f369a08749f1f` |
| [`morphogenesis/experiments/L1_field/x79_mix075_s178.json`](../morphogenesis/experiments/L1_field/x79_mix075_s178.json) | other | 544030 | `1eda092a62f550a94a904e0a96905a6eb84be00158f8e687d5d431b2835faea6` |
| [`morphogenesis/experiments/L1_field/x79_mix075_s179.json`](../morphogenesis/experiments/L1_field/x79_mix075_s179.json) | other | 570611 | `bf7ba41e45e9664b4ff16edeecf4cbddbfc5640e6772295dc21b75a006e45fa5` |
| [`morphogenesis/experiments/L1_field/x79_mix075_s180.json`](../morphogenesis/experiments/L1_field/x79_mix075_s180.json) | other | 512787 | `499c994ef2e6d11678e101cd136ec6c8b3fde6b00342941e902bc7a257fcdb0c` |
| [`morphogenesis/experiments/L1_field/x79_series_index.json`](../morphogenesis/experiments/L1_field/x79_series_index.json) | other | 1996 | `46e431208f5539108a45d094a4de9a6348de43f20809110d4bee8a749d023698` |
| [`morphogenesis/experiments/L1_field/x80_series_index.json`](../morphogenesis/experiments/L1_field/x80_series_index.json) | other | 1501 | `9f6db082148d79121fd98fba10ebe592f8d5b332753604825216331c07039183` |
| [`morphogenesis/experiments/L1_field/x80_w025_s171.json`](../morphogenesis/experiments/L1_field/x80_w025_s171.json) | other | 708454 | `84846eeeb04b52de0a2ee390e49368a8a900198f3caa2cd9ef2d79126d7122e2` |
| [`morphogenesis/experiments/L1_field/x80_w025_s172.json`](../morphogenesis/experiments/L1_field/x80_w025_s172.json) | other | 819430 | `7799180cd87f8cb6f3dbcd761be1fde7be55eb706e014e6425ebae7a8006fb8f` |
| [`morphogenesis/experiments/L1_field/x80_w025_s173.json`](../morphogenesis/experiments/L1_field/x80_w025_s173.json) | other | 747451 | `912ca37ddcc51ee118fcf94573f88120b093bff05abd864dc64043bb7bb0dbbd` |
| [`morphogenesis/experiments/L1_field/x80_w025_s174.json`](../morphogenesis/experiments/L1_field/x80_w025_s174.json) | other | 729456 | `edba6883b2fbd53ef71697c9f4172aea19c38d3b9f5aa566e1756154f386cf25` |
| [`morphogenesis/experiments/L1_field/x80_w025_s175.json`](../morphogenesis/experiments/L1_field/x80_w025_s175.json) | other | 785737 | `21d61d8b13744dc90978578a0799f7c07538218ea825f4ba4e978be1bd68cc0e` |
| [`morphogenesis/experiments/L1_field/x80_w05_s171.json`](../morphogenesis/experiments/L1_field/x80_w05_s171.json) | other | 529489 | `e99b47fc2d7873e617339033feb756e225942cb4edbe9efa25e0a44746f873e9` |
| [`morphogenesis/experiments/L1_field/x80_w05_s172.json`](../morphogenesis/experiments/L1_field/x80_w05_s172.json) | other | 575601 | `58fc0978f28593d456c6ea4992ca58deeeacd47e808a38591a784e23b89cf8da` |
| [`morphogenesis/experiments/L1_field/x80_w05_s173.json`](../morphogenesis/experiments/L1_field/x80_w05_s173.json) | other | 513627 | `4ecb04a67d413e4a63dd92f374101def98ddf16accf41318789dcf9a3d9ffcb3` |
| [`morphogenesis/experiments/L1_field/x80_w05_s174.json`](../morphogenesis/experiments/L1_field/x80_w05_s174.json) | other | 620880 | `50edd8174a5c76a0244520ba3da556eda64980648a13bb4631f920468e614d47` |
| [`morphogenesis/experiments/L1_field/x80_w05_s175.json`](../morphogenesis/experiments/L1_field/x80_w05_s175.json) | other | 676016 | `635fa9f68f54df0148310d8c0fc453925a89e9d87d387d320512b19637b77179` |
| [`morphogenesis/experiments/L1_field/x80_w075_s171.json`](../morphogenesis/experiments/L1_field/x80_w075_s171.json) | other | 567608 | `40b1477e13bbd894d5ff9f404506674ffd52994aa44d8a102b88fc5e84f4ffbf` |
| [`morphogenesis/experiments/L1_field/x80_w075_s172.json`](../morphogenesis/experiments/L1_field/x80_w075_s172.json) | other | 561929 | `eb7f347a4f33ceb201b3a5a48ef4865b5dbb8e2e4af975300ef94a1df7f4cee3` |
| [`morphogenesis/experiments/L1_field/x80_w075_s173.json`](../morphogenesis/experiments/L1_field/x80_w075_s173.json) | other | 450985 | `a6d8ad8f9b471014f522a6eed727d4e8b96534ad311f009b544df158e4750d6b` |
| [`morphogenesis/experiments/L1_field/x80_w075_s174.json`](../morphogenesis/experiments/L1_field/x80_w075_s174.json) | other | 519299 | `c8d6b03aa3c3e0716f78509f24d97dbad3fb08b8b810ea3f7e1e9865da85fd67` |
| [`morphogenesis/experiments/L1_field/x80_w075_s175.json`](../morphogenesis/experiments/L1_field/x80_w075_s175.json) | other | 622174 | `8acedd04edf6ae89085dcb462e00bee01cc4f50db056149b6253543ea2c531c4` |
| [`morphogenesis/experiments/L1_field/x82_s0_q11_s181.json`](../morphogenesis/experiments/L1_field/x82_s0_q11_s181.json) | other | 919705 | `c04c9562ca89f5c27e2ec1bfa93a618f1c9787fc0e8434701648c93b817df161` |
| [`morphogenesis/experiments/L1_field/x82_s0_q11_s182.json`](../morphogenesis/experiments/L1_field/x82_s0_q11_s182.json) | other | 950372 | `4cf42cd88488a2063f1a51f9e96d37df418e2cd07cbe69990ab3b3aa1b880229` |
| [`morphogenesis/experiments/L1_field/x82_s0_q11_s183.json`](../morphogenesis/experiments/L1_field/x82_s0_q11_s183.json) | other | 941373 | `0140a2868921835cb9644fa708cfefa9a1051d72500f763044c774240c2d8415` |
| [`morphogenesis/experiments/L1_field/x82_s0_q11_s184.json`](../morphogenesis/experiments/L1_field/x82_s0_q11_s184.json) | other | 947901 | `18ec776d67d89c8bd61507404570b5c641f3d24bf174ec57645c278402261ccc` |
| [`morphogenesis/experiments/L1_field/x82_s0_q11_s185.json`](../morphogenesis/experiments/L1_field/x82_s0_q11_s185.json) | other | 927505 | `281126375fe3d137e2ce639a0e07c46436461634d87a2dbdec5fc6c366f06b82` |
| [`morphogenesis/experiments/L1_field/x82_s16_q11_s181.json`](../morphogenesis/experiments/L1_field/x82_s16_q11_s181.json) | other | 483679 | `44119caf2ede42f31bb756262fe28499b852f2ee03faba19dc7f1904235394cb` |
| [`morphogenesis/experiments/L1_field/x82_s16_q11_s182.json`](../morphogenesis/experiments/L1_field/x82_s16_q11_s182.json) | other | 561722 | `d827dff8a43663c1fd5614b9b3bffb0b9033cfd46439e3cf751cbc42d696316a` |
| [`morphogenesis/experiments/L1_field/x82_s16_q11_s183.json`](../morphogenesis/experiments/L1_field/x82_s16_q11_s183.json) | other | 527553 | `6121328b4534acf2ccb5a518029b1bee6fc4915f966928716121fc645d7864a0` |
| [`morphogenesis/experiments/L1_field/x82_s16_q11_s184.json`](../morphogenesis/experiments/L1_field/x82_s16_q11_s184.json) | other | 457370 | `11583e3d5c102e93864e70551580a215e0dde43a962dd010d85ba14f43a116e2` |
| [`morphogenesis/experiments/L1_field/x82_s16_q11_s185.json`](../morphogenesis/experiments/L1_field/x82_s16_q11_s185.json) | other | 475548 | `60fcecd5e89470efb9db36e674351317eebdc5ac5ddb8671bf27ab019dd70a86` |
| [`morphogenesis/experiments/L1_field/x82_s1_q11_s181.json`](../morphogenesis/experiments/L1_field/x82_s1_q11_s181.json) | other | 588312 | `0ecf0713c819fedfa6e2d99e65ac928b852fbd4f1e011de35c0eb4afda8b57c4` |
| [`morphogenesis/experiments/L1_field/x82_s1_q11_s182.json`](../morphogenesis/experiments/L1_field/x82_s1_q11_s182.json) | other | 512520 | `3ed700a855bb9f700677729537cde0d1c5af37a8a8d58c2066cf599b1e1947bf` |
| [`morphogenesis/experiments/L1_field/x82_s1_q11_s183.json`](../morphogenesis/experiments/L1_field/x82_s1_q11_s183.json) | other | 575612 | `3a51fe6fb3d336bc8ade05f4931e7db0fdadaa0a7738bf361f6a63f6e30c58e6` |
| [`morphogenesis/experiments/L1_field/x82_s1_q11_s184.json`](../morphogenesis/experiments/L1_field/x82_s1_q11_s184.json) | other | 517507 | `9a1ef0460d36d8f99245e46260ede879afd1bff89a24159add28511db2fe912f` |
| [`morphogenesis/experiments/L1_field/x82_s1_q11_s185.json`](../morphogenesis/experiments/L1_field/x82_s1_q11_s185.json) | other | 599667 | `6e3776182398df3fdc82d208d2cc7f092d4d4aec19150b7e1d34d477b125e6fe` |
| [`morphogenesis/experiments/L1_field/x82_s4_q11_s181.json`](../morphogenesis/experiments/L1_field/x82_s4_q11_s181.json) | other | 547784 | `881264dd13cda9d2d7d778e8541cf1996dd7cddd99894bb8d03b17caf93717ba` |
| [`morphogenesis/experiments/L1_field/x82_s4_q11_s182.json`](../morphogenesis/experiments/L1_field/x82_s4_q11_s182.json) | other | 466257 | `0ea720f2894c377540b10bcf95d706cc014f792b4251d4af5ae1cdee9a17ff42` |
| [`morphogenesis/experiments/L1_field/x82_s4_q11_s183.json`](../morphogenesis/experiments/L1_field/x82_s4_q11_s183.json) | other | 513357 | `207838a8225996b90cfceb478bb893594254f5caf856316e88dfe437fe12481a` |
| [`morphogenesis/experiments/L1_field/x82_s4_q11_s184.json`](../morphogenesis/experiments/L1_field/x82_s4_q11_s184.json) | other | 438270 | `e6837b603a58b190d714bfba13b619da117760f47069d5c3883f107efbfe85e1` |
| [`morphogenesis/experiments/L1_field/x82_s4_q11_s185.json`](../morphogenesis/experiments/L1_field/x82_s4_q11_s185.json) | other | 500771 | `d0ae9149d700616468523bd72c58bb56a26e875ab4b190f0d980bc300e2b72d1` |
| [`morphogenesis/experiments/L1_field/x82_s4_q14_s181.json`](../morphogenesis/experiments/L1_field/x82_s4_q14_s181.json) | other | 426754 | `557def9b8cc0359241a87d0f6c2d80b3b03e637eeebbb97baf7f4101a55eb258` |
| [`morphogenesis/experiments/L1_field/x82_s4_q14_s182.json`](../morphogenesis/experiments/L1_field/x82_s4_q14_s182.json) | other | 572628 | `4c8d646196b84c5ad7946095eeeaac0a0e2d9d4893b93af5631d10d6c3180155` |
| [`morphogenesis/experiments/L1_field/x82_s4_q14_s183.json`](../morphogenesis/experiments/L1_field/x82_s4_q14_s183.json) | other | 549572 | `e48564bbd60609a0db5da12605fbb7e40ea81b8b4f1ca9035fc1cb2725d13fff` |
| [`morphogenesis/experiments/L1_field/x82_s4_q14_s184.json`](../morphogenesis/experiments/L1_field/x82_s4_q14_s184.json) | other | 572130 | `82f088e6aabdebf325c21796adb2e1f0129427b35cdd702d7d465edb2f9cd57e` |
| [`morphogenesis/experiments/L1_field/x82_s4_q14_s185.json`](../morphogenesis/experiments/L1_field/x82_s4_q14_s185.json) | other | 522826 | `b3076900f9ee6d3410ab57689af1e68745ea2a39dad5a3c061f0f867fbf1fb16` |
| [`morphogenesis/experiments/L1_field/x82_series_index.json`](../morphogenesis/experiments/L1_field/x82_series_index.json) | other | 2559 | `f40ca596958ed3b4247a0545b1ef693fafc4dc1b4ea140f9ef88ce17572ec729` |
| [`morphogenesis/experiments/L1_field/x85_f025_pattern_s191.json`](../morphogenesis/experiments/L1_field/x85_f025_pattern_s191.json) | other | 800080 | `f7242052f37f88e5c059dcfcba8caea33158c5b12970892f182cdcbd1b78aa32` |
| [`morphogenesis/experiments/L1_field/x85_f025_pattern_s192.json`](../morphogenesis/experiments/L1_field/x85_f025_pattern_s192.json) | other | 808758 | `0805462a5ee6fc3123b40c755572a22fbf902adbf06143062ea482d04e9eb411` |
| [`morphogenesis/experiments/L1_field/x85_f025_pattern_s193.json`](../morphogenesis/experiments/L1_field/x85_f025_pattern_s193.json) | other | 737997 | `45d4c315cb954576c04b2026acfd4aeba118d45eec88bf8dc8cdbc639dca36cd` |
| [`morphogenesis/experiments/L1_field/x85_f025_pattern_s194.json`](../morphogenesis/experiments/L1_field/x85_f025_pattern_s194.json) | other | 791673 | `35efd27b01231a939d971a4a433db0a59960fca09f31cef55ee76cf337b27f19` |
| [`morphogenesis/experiments/L1_field/x85_f025_pattern_s195.json`](../morphogenesis/experiments/L1_field/x85_f025_pattern_s195.json) | other | 811652 | `f822939fe5a346dad84ccc7c13324908c62f76d1e2ae250e01f5f92125398d22` |
| [`morphogenesis/experiments/L1_field/x85_f025_pattern_s196.json`](../morphogenesis/experiments/L1_field/x85_f025_pattern_s196.json) | other | 763001 | `262495283a9d4820b07df579920f7b916ac031d7cf20b810c7e141ae27e8dd13` |
| [`morphogenesis/experiments/L1_field/x85_f025_pattern_s197.json`](../morphogenesis/experiments/L1_field/x85_f025_pattern_s197.json) | other | 772899 | `ccfa7939e78c395139494dda0dd04b9fceccbb6f88f8e5cdd774206429c3ceb1` |
| [`morphogenesis/experiments/L1_field/x85_f025_pattern_s198.json`](../morphogenesis/experiments/L1_field/x85_f025_pattern_s198.json) | other | 739261 | `6578e42df3d71d002f0acc1fa06e878b0ca10cefb3e53b61e1088f1b82c7cc53` |
| [`morphogenesis/experiments/L1_field/x85_f030_pattern_s191.json`](../morphogenesis/experiments/L1_field/x85_f030_pattern_s191.json) | other | 931330 | `62a27a537ae531b483e4ce5dbffe3350feaf1c615714ba1c8ab98e0d2ecdfa71` |
| [`morphogenesis/experiments/L1_field/x85_f030_pattern_s192.json`](../morphogenesis/experiments/L1_field/x85_f030_pattern_s192.json) | other | 911172 | `656e28fc26c0ac189c06e6e63169094849797be712b00f2378c46650cd777229` |
| [`morphogenesis/experiments/L1_field/x85_f030_pattern_s193.json`](../morphogenesis/experiments/L1_field/x85_f030_pattern_s193.json) | other | 820893 | `347ddbcd7f97c89c45993daed78ed250e53674d70b33ee4d41f7cc0007128000` |
| [`morphogenesis/experiments/L1_field/x85_f030_pattern_s194.json`](../morphogenesis/experiments/L1_field/x85_f030_pattern_s194.json) | other | 893547 | `ddba620f1d34b20a2aafe4b049999533af3826fab92c2d19563fadd73a1dc0bd` |
| [`morphogenesis/experiments/L1_field/x85_f030_pattern_s195.json`](../morphogenesis/experiments/L1_field/x85_f030_pattern_s195.json) | other | 896325 | `42233fc1aa75aaea12c77d2bb71839da25325a066be149b13ed645d09fdff7db` |
| [`morphogenesis/experiments/L1_field/x85_f030_pattern_s196.json`](../morphogenesis/experiments/L1_field/x85_f030_pattern_s196.json) | other | 951516 | `5b9aad0cae3f551af171842054c3306cd2376505cf25dea88d1b5d185865a2cd` |
| [`morphogenesis/experiments/L1_field/x85_f030_pattern_s197.json`](../morphogenesis/experiments/L1_field/x85_f030_pattern_s197.json) | other | 982502 | `781b276484f6e0f379085e26af89d5ba91114b288b52e4f7586dae9779c58b76` |
| [`morphogenesis/experiments/L1_field/x85_f030_pattern_s198.json`](../morphogenesis/experiments/L1_field/x85_f030_pattern_s198.json) | other | 831716 | `21e39c8a856e99d8b044cfc54f6c54952f08f95fd483cdf3a2392b45900b376d` |
| [`morphogenesis/experiments/L1_field/x85_f035_pattern_s191.json`](../morphogenesis/experiments/L1_field/x85_f035_pattern_s191.json) | other | 553373 | `3e194dbb8c97949ad8e7eb273a995efb473165f4491afe80082c3cd06aff471d` |
| [`morphogenesis/experiments/L1_field/x85_f035_pattern_s192.json`](../morphogenesis/experiments/L1_field/x85_f035_pattern_s192.json) | other | 540807 | `4dc3411758aa012b6affd5658dbbb4b6190e84d687b8c3c7e814d7bdf0b11770` |
| [`morphogenesis/experiments/L1_field/x85_f035_pattern_s193.json`](../morphogenesis/experiments/L1_field/x85_f035_pattern_s193.json) | other | 456867 | `dd7dc0fe48bdf122a1f2b02f0a8cfa0d2f26b90b9746c299ede80a40a192ada8` |
| [`morphogenesis/experiments/L1_field/x85_f035_pattern_s194.json`](../morphogenesis/experiments/L1_field/x85_f035_pattern_s194.json) | other | 475157 | `87a6fccda3891d77017b45a24b4e7060d6451f695644c5c72b70f9d97191b2ad` |
| [`morphogenesis/experiments/L1_field/x85_f035_pattern_s195.json`](../morphogenesis/experiments/L1_field/x85_f035_pattern_s195.json) | other | 541416 | `90cc0ebf51d197c93f54cf9955dca8d50cf2ff19ce8221e4755dd085d3838d59` |
| [`morphogenesis/experiments/L1_field/x85_f035_pattern_s196.json`](../morphogenesis/experiments/L1_field/x85_f035_pattern_s196.json) | other | 574009 | `e71fc9eeb7e023239be7e916b17801e5acb4f061400fd4598d09c8ed91895933` |
| [`morphogenesis/experiments/L1_field/x85_f035_pattern_s197.json`](../morphogenesis/experiments/L1_field/x85_f035_pattern_s197.json) | other | 510724 | `40903a0d492223a7d2f54baa2cc59e52a68b305243880da53c687bf9c2c0550e` |
| [`morphogenesis/experiments/L1_field/x85_f035_pattern_s198.json`](../morphogenesis/experiments/L1_field/x85_f035_pattern_s198.json) | other | 467848 | `62fc7aeaac23a55ae64bccef70501d63167fb29d34e6540121bd52c63f837439` |
| [`morphogenesis/experiments/L1_field/x85_series_index.json`](../morphogenesis/experiments/L1_field/x85_series_index.json) | other | 2407 | `fd140089ed064b862bcdde364ad099c2eddf059fdbe8dbfd86c4a9a6c5923ad9` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s201.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s201.json) | other | 743830 | `e286d754edf00ce7a7c98ef66f6c1b7427b37ccd61c949a0e11b871e1abe8883` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s202.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s202.json) | other | 749586 | `24db622ddba74c896b521117713c18cabc078d656f3f085c4495d95e4d82cb99` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s203.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s203.json) | other | 310485 | `2b03eaf4cbb85b2bb7fcaa52e9ff6364ced44a754493df04448b62e043b77a00` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s204.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s204.json) | other | 782769 | `55abf3a383ea45063736016b214e26c7cab9f8bb8e533d333a0a8157bb23a45d` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s205.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s205.json) | other | 754098 | `6d4bb677dcd227bebaf4a5e586e31c8f6d80198e857829a5c8fda2b550dfbaff` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s206.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s206.json) | other | 739961 | `58e97e745ee4d3f33a917327fc758dd609d1c267270ed3e866f7394fb7be54fe` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s207.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s207.json) | other | 747214 | `825e1856c00dc3e0c6fac16a3753a6b3826c5bc3ac93a38648ab723f3c5bb027` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s208.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s208.json) | other | 687331 | `83382035711c49d45577b12c22d1ec0e9ff69ceab220400835eac977be5a8c4e` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s209.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s209.json) | other | 680879 | `84f91155a8fcd8728137cf4e033ba0a3c1375a9be872bd1ba1d3513784b29368` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s210.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s210.json) | other | 343931 | `25878ac995f0e463cef9658fa4aa430fcd43f71f02932045ea05ce9d255862d0` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s211.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s211.json) | other | 745311 | `f0534a492b66ed5ab2aef06d973677cfb5227d333f33cee8a2ce27964bdfd9ca` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s212.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s212.json) | other | 680369 | `a3ff40617a31863029fd3d76076c2b7395126153d15168e03fa65f4645b4ace7` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s213.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s213.json) | other | 286538 | `13c410b5d01d51c14c5281d8b0b5f4f314fbf491bbd9b29765c9e56ef009e2d8` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s214.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s214.json) | other | 767649 | `122822dc4bbbf44739039f4cce456371c294467c6ac8e7cf69ad565fa43350fb` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s215.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s215.json) | other | 534978 | `d44b997c43acc9306a07748ce873d82445e72ce748f516a14601be0fc3c35f58` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s216.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s216.json) | other | 744255 | `7949853e9254fd2a36aeb24087dff6db81088d289d542d39bb06a294cca9de80` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s217.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s217.json) | other | 749148 | `4ac3116eb62750356392549334cc8a49e22878ccc6233364a775feb01c401b07` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s218.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s218.json) | other | 680204 | `fb7ef139a864c1766af5438bd9d5910367f2cc7abba8039b0bc615e1a1507801` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s219.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s219.json) | other | 757265 | `066c9032f7a01f63619a2d893ca1e42224376382bfced17614512eeeef725bbf` |
| [`morphogenesis/experiments/L1_field/x86_f025_pattern_s220.json`](../morphogenesis/experiments/L1_field/x86_f025_pattern_s220.json) | other | 333794 | `cd247b967f305ef3dc97cc3aa4c29d26d6973e373c1eb5310a2cd86fadf9cda0` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s201.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s201.json) | other | 856665 | `9b56470a83765317ff990e238fd2f383b5dfe20f60ca3500d932b60e2162ebf3` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s202.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s202.json) | other | 872137 | `b1499fabb1d733e5235d95ba2797949f710b17dfd0d562f0cadad90d4452658a` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s203.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s203.json) | other | 858505 | `d538fbc3b55e5799a05a29822795f55de1db4d21d91ceeb7932a9f6466aa6e36` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s204.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s204.json) | other | 960508 | `188f522ec4fbc7e0d1591e0a2e123104a54915aed6194767cdc597cefcf5e632` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s205.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s205.json) | other | 750540 | `d2003be50978ddeca89511cea92bdc42703d0def3171662f335e419110f2b8c5` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s206.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s206.json) | other | 893628 | `845562639459fe3775cd2c70f8d7472ce5b5747d50b687183e175a9da7ccbf16` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s207.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s207.json) | other | 883202 | `4afcd0a154e3e843552d0abf9a00c856f203665299ab6a4e8b55edab90c85873` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s208.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s208.json) | other | 830313 | `021553c484a194700849f4cf75a260bb1f4ad28b769f7963eafb9ba901729304` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s209.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s209.json) | other | 739169 | `703d15e8da4f51a10ea8d9b2b85f476736521d7bec2d719338ca5ea81d88b8d6` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s210.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s210.json) | other | 896996 | `9d6ce9855bc0fd864366b4b131232c1ba9ebeb222f2952347da93b8572b9f5dd` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s211.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s211.json) | other | 860242 | `7ebe4c14ad2ad129426563864bd8e4bc0a24775846004f5950ebe48d7b2ee9e6` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s212.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s212.json) | other | 738841 | `6f32f044cd9f5e40a6fac24d1def2d609c9b79c77b2782a17024b609aab2be79` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s213.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s213.json) | other | 904230 | `0db77e5d5aad397eaf67078dfc37b1ab96d100e14011384e4ebc9986537384fa` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s214.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s214.json) | other | 842944 | `9925d290d2d399c65faf6ac00b2538a13f6a793473fa47f7f9b6d37973d18e67` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s215.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s215.json) | other | 880114 | `982ecb109cec6783cd24dce4d05ce70a9d0da6a949bf9dafc7b3995e6a465365` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s216.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s216.json) | other | 857202 | `45e3b169b9234f38b9137d883369317ada1da25e3a3659ffe1143088fd56f15e` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s217.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s217.json) | other | 872598 | `ff7f097892e94cc8c926fc578413907dd0fe32362b238fc6ba7031389e224d20` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s218.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s218.json) | other | 738646 | `84a23e5b9a1b4ad227295c3539ae44ac08f1f24b53ec5af7c3e0151eafa0da73` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s219.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s219.json) | other | 750696 | `c0e3f05f40fa36b0ff4e6b7cdc7cc2a907249e27d3e16e87b7b3bd0fb763abb6` |
| [`morphogenesis/experiments/L1_field/x86_f030_pattern_s220.json`](../morphogenesis/experiments/L1_field/x86_f030_pattern_s220.json) | other | 888047 | `49638437686ac9ebf6da26fe2cc4fc2d68d9dde1d5158442b36723c173c925ad` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s201.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s201.json) | other | 500717 | `3e4ebb2485c5c34672db5c8f7bed85cb9fcbe20297c3bccb728ff4b3e0b7a0a3` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s202.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s202.json) | other | 455168 | `36dbf4070c7e660d220265d979d17aca3219753b871e195add875328438d2644` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s203.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s203.json) | other | 662980 | `34cd2097657b1b27566c6d7931ecb25b4b02118e099efc4f47dbc7bfd10efa92` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s204.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s204.json) | other | 640785 | `4d98ddb404c989a148425115da1171b801be7b125afb31cb8631c4baf040a6f4` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s205.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s205.json) | other | 409426 | `dbdb718c6b7ca4255b049771fc85dc7f81d17860dc866baa5a1f0178326cb2cc` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s206.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s206.json) | other | 495536 | `d2bacee022e153652e0c94c772f3e0a7de391ac49248215a3d2aa64c03a9965b` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s207.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s207.json) | other | 505532 | `f78a1b1327c5fc7603b7623ada82caf2ab9088d13cd5c27fe23a3ccd08e67984` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s208.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s208.json) | other | 557222 | `9975111eff222f606e4b8740ec5a5f121cd56236e8c3df665f14c3d88616c2b8` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s209.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s209.json) | other | 467409 | `ab4c949253f2fc8592ca4a8f8e101065a97cd86993378a60b89d65cfbb7c6a72` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s210.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s210.json) | other | 569715 | `0d132dab7ea5c3f35768ee8543eab77fa294a4df1082f24450a4d2651ac22aed` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s211.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s211.json) | other | 578479 | `f650be615f4d6b99249cfabaf5c70d966b7e5b02225c4b5cf15bdc3b5e7747fb` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s212.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s212.json) | other | 467026 | `f388d81662774a171cc84014876f8cf36f16ddfe3936305dac0c2e2f588c48f4` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s213.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s213.json) | other | 539156 | `6f35df2a76d507a2af8dc383e8a382e57a186f4f2e51eb072b9203595b8d8000` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s214.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s214.json) | other | 539503 | `25ee3bfcd99adb4635a2c4d1ee84bf91eb04c44ddb12c6f67ad3bf1b0c775b59` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s215.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s215.json) | other | 581283 | `fdf4057bfcae4ca703a6f2d80a337363d97d1012c3f4354beafebc6097b1beaf` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s216.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s216.json) | other | 500687 | `12f791b459f9f332be7a23b1873c9eb0d8b4c9aa5489ef6dbbbccd41386323bd` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s217.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s217.json) | other | 455249 | `2504b01882bdfa1a17cb78064fb75f652f47368b33710edac0a28521d3164fc1` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s218.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s218.json) | other | 466837 | `9f85b259aac96478c1d24719e7bd6e5ac6ac2b4d6408c6f8ab4c48d1b27ba874` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s219.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s219.json) | other | 409343 | `97c6c0c6838fad430517d519a8a3dd96d2c11cbd1edcd73f2bced91ecc658abe` |
| [`morphogenesis/experiments/L1_field/x86_f035_pattern_s220.json`](../morphogenesis/experiments/L1_field/x86_f035_pattern_s220.json) | other | 603247 | `0752af327278889d63d1d3dc4176dcf4714aeacdd4c9668dc8a3831fdb7be7fe` |
| [`morphogenesis/experiments/L1_field/x86_series_index.json`](../morphogenesis/experiments/L1_field/x86_series_index.json) | other | 5942 | `6fe651433abfdaeaf7579206a56db97fcffbfa221e8db202261b3a2527a17efa` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s221.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s221.json) | other | 737742 | `45dcfa31eb5b8e413891d1d150ac81c8dab1ac23b28917e83c7a1c0dacc3b1ee` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s222.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s222.json) | other | 812797 | `557496455328ad929b0b008fa5a55849b59b78cd7d80776aeff4808e07ed41ae` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s223.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s223.json) | other | 763279 | `a49824a22b33c56983cec60f649ab5edc7fbb67d45824aa8e9e7f77579a4baa8` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s224.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s224.json) | other | 756179 | `a9c19b1b51795df7911f7a42fd2350a56b54e26072ad84127a4ca1a6eae3c184` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s225.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s225.json) | other | 805344 | `a9839dd65eac6edf10a3d8a24675b7f1a53ed4859258c37a954753d6f3b918b8` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s226.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s226.json) | other | 788226 | `f53e9e5147023bc1358235520a8c6d5d7986ef382adc4cb19bc1f3c6bc99458f` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s227.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s227.json) | other | 804630 | `a6ce213c5af881db497146fe405b1ce1f38308f18079c80cfcae0034d958b819` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s228.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s228.json) | other | 793839 | `bbca6b5cfb2c83dfde159a67f5eeec7b16d9e040cdf81e5f5aa530da4d25bd09` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s229.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s229.json) | other | 777270 | `0f6a424bb81932ffc7b48ec1394718986dc0adbc9b7a760670c1c194a80f4ec8` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s230.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s230.json) | other | 814064 | `8b8f0872e3e58cd053e011d9dc433566308adae283b61472c97c9caff5ce37aa` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s231.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s231.json) | other | 804943 | `5ce0034cb10dcbba2c936eddd59f6f4d24a8e5431a6553fb31314ab3d0be7fd5` |
| [`morphogenesis/experiments/L1_field/x87_f025_pattern_s232.json`](../morphogenesis/experiments/L1_field/x87_f025_pattern_s232.json) | other | 593145 | `17446c0971885e1920ad088a08a7468e8f577514ecc1e93b4f0552faf545b554` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s221.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s221.json) | other | 782521 | `ac33f931b868fe539cb1539dab6f968ee86668a44d8c7e25bcef365fc4d12b11` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s222.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s222.json) | other | 905255 | `1d77a14a815cbce0fedcd0d87b046f82bcf43d4a992363286cde850cad2cea37` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s223.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s223.json) | other | 1027085 | `c844f8c25b2efd0967ccde30b6de1eb1d1ab7661f614552f8b3a79b8f0d07ad3` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s224.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s224.json) | other | 759887 | `4f493dc42ac1440b45a6b13d10ad92c0f0f9925765346504c932fb7b8823dcdb` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s225.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s225.json) | other | 844943 | `dacac9e784d17fbfb8237ce0729ca3f5e2ef20d7dbd197327f339dce475a32bb` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s226.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s226.json) | other | 1010022 | `c5c4180e70cfbccfbb46c0c5272ca000c7e7ca6a60be9ba9b83d8a329c8dcb17` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s227.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s227.json) | other | 919108 | `13268b965a8468e835632eff427bd325c5cfec23a62622d5eb9cb542f4c34024` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s228.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s228.json) | other | 924944 | `49c46635cd6791c89aa396abe1bf5a6d677446f1100659568764f5eab36f9db4` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s229.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s229.json) | other | 884941 | `f7ac08b843bd0b76f82b75f6725ce7ef37bada49e29dccb4849637b1112baf04` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s230.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s230.json) | other | 1021501 | `ac6d987e8cbd521fef2766fa39a2d7faaf4bcbacce93ebac4df350742d5109c4` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s231.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s231.json) | other | 844502 | `f8f7be0d540bdb223fe035f24eb7375372e6705fb73463d619cc853dc05b6ccc` |
| [`morphogenesis/experiments/L1_field/x87_f030_pattern_s232.json`](../morphogenesis/experiments/L1_field/x87_f030_pattern_s232.json) | other | 969584 | `0cbf4ec328f676a97bc8e1c6f141b3d2ea68b705b4135c61337ca8d82450dc35` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s221.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s221.json) | other | 505557 | `0f167b7338745937fa2580ec3ddcea05e8032c6247c229e499715b8c6e768b52` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s222.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s222.json) | other | 549455 | `cdfbff5beb63645d3537c53ef4f4e69c687696c44ce596adca97078ab9393cd4` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s223.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s223.json) | other | 635296 | `5f2b7ab9ea640d4426e0b4ee19985743b8920f9edaeb4cf220a29b024f31c33a` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s224.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s224.json) | other | 576089 | `8d8b629dab0881873eacc7eca26573b6dcb9210e7c2f8567e3fa3b1a68c22c1b` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s225.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s225.json) | other | 543992 | `1746d9be7fcee0cf72adbd5d705c30595c6fca9b855635f9e2d260f429a485dd` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s226.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s226.json) | other | 511280 | `796fdc9e271a0a2b25d67030385d69a65f5983e1fcf3f77b0cb5287c88326cb2` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s227.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s227.json) | other | 485572 | `873a0e2856dc769f797d1ae004d60dbfaa6f05cd348e8cec9397c5f918c48a6f` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s228.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s228.json) | other | 624962 | `225869e21fc5074e91fea7e8066d3a86c9ff4a7f5bc4aaa5958670e73906e489` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s229.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s229.json) | other | 645122 | `b3d4b631527c360026c197971f0605c9a28ad1ba9d0ccd0d281bb6ece2838a8b` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s230.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s230.json) | other | 677180 | `1f28958aefc3174f5f56823a3a41e4c7aec0b049a80b85248accf26c93c95044` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s231.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s231.json) | other | 543815 | `240562ee8f141799c4ec684e5f2f3dee52d700c8a7841332a4c5b06115d0a118` |
| [`morphogenesis/experiments/L1_field/x87_f035_pattern_s232.json`](../morphogenesis/experiments/L1_field/x87_f035_pattern_s232.json) | other | 541488 | `6cb026c2427c07bd438f05bd935656ce4e4ea64f6ba91cf796b019195527f0fb` |
| [`morphogenesis/experiments/L1_field/x87_series_index.json`](../morphogenesis/experiments/L1_field/x87_series_index.json) | other | 3588 | `96eb296e0dfb097f2cd2727c80bcc4ecbde3ed8a5c7e0c86480f9bbb7616a867` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s241.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s241.json) | other | 202074 | `620b287c1230e3718c8ef20020bf407fb96286b7fb3735bbba0c254c39153e0b` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s242.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s242.json) | other | 217493 | `9b371f0005609cd5029c61b7c0f19e9ae28e9f6c719dac026aa5d1d63601b078` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s243.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s243.json) | other | 204070 | `dbfbfe2f50543ed31a6b5dd72feba0058ca13445d93162818215b5c91a6a3af3` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s244.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s244.json) | other | 302276 | `230a999faaf4de3b37fded7e4de142ef900769d3c1709d8f03a3f90a7db1acfe` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s245.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s245.json) | other | 220148 | `8793f494d2db67f324e9505cfc7eeb8f6128392efb600f42a0e3ceffb930d6c3` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s246.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s246.json) | other | 182369 | `8185b5602cc3faa8b1cba1e4752aa5fdc892a4008d094cbc1a379f7ce6e1626f` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s247.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s247.json) | other | 201928 | `df581f13e16d3f812f6e5fa07756e7ad872d2ec63e932b86400bc57641361571` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s248.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s248.json) | other | 276353 | `75d6b710710a18820d9d40db86003ee750beeb415e8f26cd06a7ef3a7141e0f8` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s249.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s249.json) | other | 184981 | `274d77c93cc63b313b92c6caaae0620b2ec5190b302aadfcd3bd713b009c9ccd` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s250.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s250.json) | other | 183202 | `f2018050208359d8a2b265d7fddacf5b0121022cb9456c730e60537bc26d858a` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s251.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s251.json) | other | 203682 | `d87da5182941efdf0b78e7f9f110de56356dade529435feeb3d46b218accee05` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s252.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s252.json) | other | 201850 | `6816a791f35644e064c4c788c138a07b472be6aac6b7d7d596360ad68ebc53bb` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s253.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s253.json) | other | 271258 | `52fb3e09423c45e2ac8fc9e7e4fb37ac7658a3052f3ccdd6f109d1b6031fe157` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s254.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s254.json) | other | 220001 | `ae2ba0b21f11dbcc03e0944a53524087ebf0a758c53fd1aadea2fb18532f1eb3` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s255.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s255.json) | other | 182382 | `9392c9c827efae27b0a0730e11e8b5d9e53184b55f80190f3a2afef74db59770` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s256.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s256.json) | other | 224617 | `792aafaa5e3193acd531e7c5c85f5754daa89577e286a9429071ed69fa0c818f` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s257.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s257.json) | other | 181793 | `d7c89a8b9d6c13d6dc52df9845397c65fc9a93232e171d95e8b418a8de22a515` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s258.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s258.json) | other | 184992 | `814f7cb3cbbb26ca934307bd356927defa4cf525ddf9a84fd29eb39aa9b2276a` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s259.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s259.json) | other | 276275 | `ad7c4de047b0ab7341cc385030e4b2a43e66552dfdab2445b735774409de81da` |
| [`morphogenesis/experiments/L1_field/x88_f040_pattern_s260.json`](../morphogenesis/experiments/L1_field/x88_f040_pattern_s260.json) | other | 259634 | `a30635e51a1f3cb088f0c537f0876f787ce2da2ffc77f08313f2c27ddf4ce64b` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s241.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s241.json) | other | 68598 | `1418cc9dbfa5055ab64d7b4707d8cb200dc00be4c6b6fb47b813bc4d531152d0` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s242.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s242.json) | other | 73959 | `b6be4e8daad2ae2d8d1a3dfecb1b5591083ba8d61ef545746c1078aebf805add` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s243.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s243.json) | other | 67807 | `c1d160b79b4c0ae06a2d8f0612e7e606690573166c3c98089d21ab91f2492461` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s244.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s244.json) | other | 83081 | `d359426fdc4be4bf9a7ae78b3364f51d5d315e317f007af9412c24cbbc2f2f30` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s245.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s245.json) | other | 66391 | `ef5a01356711032c98bf8a3e81296abb758b512b864362453db32b9f5dc53884` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s246.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s246.json) | other | 67929 | `08e0fff3dd1b8e9c6b3c2cf2adcbfe285eb1183822eb3f542e76a1cb92e1e009` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s247.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s247.json) | other | 68601 | `02263e61921d5d63552745f0930af4552884239b7d089422d48925306befd26b` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s248.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s248.json) | other | 67665 | `d7fafde101b5d8fc82761d4b6f9f45133b2362ac31333144ea3068a905220cd1` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s249.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s249.json) | other | 75548 | `fb4db635cc6d3d55fe48a736112dbf4cb8166b0e492a987bb6ae7a343ea06402` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s250.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s250.json) | other | 66852 | `0375afeea75d82a84e91b8d23c20d6a31741770278e2742a78389d8d75b87f6b` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s251.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s251.json) | other | 71654 | `50932e0f67afd49135e3bc08dd615d218862176840bbc27dece8a7b8110351df` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s252.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s252.json) | other | 68589 | `b22843fe67208c8d7f188c34d746cd3b8af117327c804edb910c85ef37b84d3a` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s253.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s253.json) | other | 68683 | `ad015c705b895af9e78898a25cc32496cbe97b7ff3a1d52b1fdccf5e73272e89` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s254.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s254.json) | other | 66290 | `27e5d03869aceb4d0075d238144af39fa8ee0761e5cff0205f7012e1d41f8971` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s255.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s255.json) | other | 67915 | `da7275b69116a8cea437ffb2e4913ea4eda3a41fca3d07475aaf4358d72322b2` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s256.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s256.json) | other | 70725 | `da8ff4bf937e760d3cd3d6cde75c246c75077b9eeb3d2e307594075a52b2e811` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s257.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s257.json) | other | 66984 | `adce1c5e89949fe0b6f4d739c5c347b69c9b9650dde347195399bd1c826e0949` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s258.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s258.json) | other | 71845 | `09ae5ffb12d4a286f36241f43157f2a53cc8720b0a8632063dafa1c3a9b9c96d` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s259.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s259.json) | other | 67740 | `3ca1ccf722382534b49ec3b243ea6970a84b406f6c2e1f6af93b6d26900db1df` |
| [`morphogenesis/experiments/L1_field/x88_f045_pattern_s260.json`](../morphogenesis/experiments/L1_field/x88_f045_pattern_s260.json) | other | 71754 | `efce89c29e8e1534f2d1ccf3c1ce86636c436995f3631044115c21bf480c4a1b` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s241.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s241.json) | other | 60819 | `3cce93d443b7e00dee5109d06e79db5bd59c2de3fceda62160545da6a40a1c13` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s242.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s242.json) | other | 60786 | `11d05fe3f6ce49f7d099e8da6253268645d83f566e97fcf63beb40c6ed9ae4d6` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s243.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s243.json) | other | 60839 | `9e8ac5d014807527a9cc164cf8f8ee559db5080d7ff8116a1d424348bf9a9a47` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s244.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s244.json) | other | 60770 | `4b532ab3a808eb1ce3790ad75293daad487ab6623008bb636c604debaf260793` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s245.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s245.json) | other | 60810 | `e131de9921529a08038b4ced7297da87103a6e7e0642cf63d178f9f7690eb73c` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s246.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s246.json) | other | 61499 | `3d524cc3c6e9312f2e4402d2ecfc74014f953054c29dbf7eda505ca8289e748e` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s247.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s247.json) | other | 60817 | `29966ede781cc92680308634244defba7b56bfbcfb839f378a5941b776ecb9c3` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s248.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s248.json) | other | 60735 | `2e71cc8e98520c06c89c7fd02acb87ebebc93d7153040c1778ae71c52addea6d` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s249.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s249.json) | other | 61506 | `d5bfbb772dad31b516003613fd92a8c8a20b08f4766454ca996b6b2376f0fe08` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s250.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s250.json) | other | 60817 | `37dbe126270b1774ae0fe5098f2383beaf5f30eea31ff4f157da4795c7bfcfce` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s251.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s251.json) | other | 60818 | `3c66f9747f8385a6d440cacce98e9f10b2309fc6ce9d78fcf42f0bcd2c090e0f` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s252.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s252.json) | other | 60827 | `4aafde6c2c7b7d17f688e7bae74895b91cc8c6f626182f2a8e9f270b0c694e0d` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s253.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s253.json) | other | 60546 | `d37eabe6b917005234d8955d164794aee56b6b51c007efec0ad13cb551e3eda0` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s254.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s254.json) | other | 60581 | `97f8aa03de5cca2df4428bdac2febc02d46c1cb411ebf5142931d7d3a66305a5` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s255.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s255.json) | other | 61519 | `ecfdd153ca814f47dd32dd045e324793429c85dab949be132b1ec2ddfe1568bb` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s256.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s256.json) | other | 60823 | `dc212cee3ad65f9ed3b944113b2e66d74bc14d0d26ee5aad086ae471125cc646` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s257.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s257.json) | other | 60816 | `2e1ce03c74d961a5e82462a13fae3034952f757c5d31e927b7e587d3d01b2bf6` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s258.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s258.json) | other | 60809 | `e4f2a390df4bef01ec60cb4ffcdf5ff14ee7e2af98569bf26d03b9f208759114` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s259.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s259.json) | other | 60737 | `486295756a240739965cd608a9e5f0a341f74733c5186337b354320a292f58e8` |
| [`morphogenesis/experiments/L1_field/x88_f050_pattern_s260.json`](../morphogenesis/experiments/L1_field/x88_f050_pattern_s260.json) | other | 60792 | `8ad54dd293edb1e53df16acf3029684d5189562be98b59b6dc91126675c4baf8` |
| [`morphogenesis/experiments/L1_field/x88_series_index.json`](../morphogenesis/experiments/L1_field/x88_series_index.json) | other | 5952 | `021499920d3b0732069bb6dc4709901f23e917c09cdffd6d59223ac6bc340bc1` |
| [`morphogenesis/experiments/L1_field/x89_f046_pattern_s261.json`](../morphogenesis/experiments/L1_field/x89_f046_pattern_s261.json) | other | 64351 | `a0adece552742f1cfaa02816a90912c98b9da67438e87f75d4bc34b7862593d2` |
| [`morphogenesis/experiments/L1_field/x89_f046_pattern_s262.json`](../morphogenesis/experiments/L1_field/x89_f046_pattern_s262.json) | other | 62751 | `b6a44221e0e6ea913c4b7ddfe144cd61bb624f3561f89898921cc2fb490a6a1d` |
| [`morphogenesis/experiments/L1_field/x89_f046_pattern_s263.json`](../morphogenesis/experiments/L1_field/x89_f046_pattern_s263.json) | other | 66351 | `51e7c5655afc4567e6a73f55625b8ef5c0ce6ff2f4a8c4e378fcab33b4a92af7` |
| [`morphogenesis/experiments/L1_field/x89_f046_pattern_s264.json`](../morphogenesis/experiments/L1_field/x89_f046_pattern_s264.json) | other | 63763 | `391b58074c3c507566083e0584394cdbcbf7e3750c78d05173ae13ba504e419c` |
| [`morphogenesis/experiments/L1_field/x89_f046_pattern_s265.json`](../morphogenesis/experiments/L1_field/x89_f046_pattern_s265.json) | other | 63429 | `8b71e715a9551b020b9530d49a09a789b7623af73c25e7a648631f895e6b4142` |
| [`morphogenesis/experiments/L1_field/x89_f046_pattern_s266.json`](../morphogenesis/experiments/L1_field/x89_f046_pattern_s266.json) | other | 64359 | `88f05ff605070114ac7269b86ef73e0c625aaa1b4ed81877689833ffbaee932e` |
| [`morphogenesis/experiments/L1_field/x89_f046_pattern_s267.json`](../morphogenesis/experiments/L1_field/x89_f046_pattern_s267.json) | other | 64521 | `6e181e267185cf45fb3756597ea1b1515b34b08c1ed386f7e2ac17078948dfcb` |
| [`morphogenesis/experiments/L1_field/x89_f046_pattern_s268.json`](../morphogenesis/experiments/L1_field/x89_f046_pattern_s268.json) | other | 64528 | `c235ffc5f25ac310b9384ac71dda1e24f9189b04e9517dd1ee543112547ec7a4` |
| [`morphogenesis/experiments/L1_field/x89_f047_pattern_s261.json`](../morphogenesis/experiments/L1_field/x89_f047_pattern_s261.json) | other | 61884 | `ffc6f0420a7ec500d3a24f59561e3657edaa2767acca74f517c5d44d9cf1c4e0` |
| [`morphogenesis/experiments/L1_field/x89_f047_pattern_s262.json`](../morphogenesis/experiments/L1_field/x89_f047_pattern_s262.json) | other | 62316 | `6e23823368832523ce0b7e5390788080c951c7e207614710aaad06da0111a6ea` |
| [`morphogenesis/experiments/L1_field/x89_f047_pattern_s263.json`](../morphogenesis/experiments/L1_field/x89_f047_pattern_s263.json) | other | 64018 | `19ad720b072725b75bb049bb1bf961c3a1676ef694d3795dbc288a0c86a20835` |
| [`morphogenesis/experiments/L1_field/x89_f047_pattern_s264.json`](../morphogenesis/experiments/L1_field/x89_f047_pattern_s264.json) | other | 62726 | `c08113b60706ef100d58edfc238db1c49b4323e3962fbb7bfaa6dcc4173fc87e` |
| [`morphogenesis/experiments/L1_field/x89_f047_pattern_s265.json`](../morphogenesis/experiments/L1_field/x89_f047_pattern_s265.json) | other | 62456 | `1b9c4d4103f29b2df4b6d6709dfd9d873170fee0ab7c21dec168875d3ae8fbde` |
| [`morphogenesis/experiments/L1_field/x89_f047_pattern_s266.json`](../morphogenesis/experiments/L1_field/x89_f047_pattern_s266.json) | other | 61660 | `2b0d14f80a3cced98b7d80b95d08a62225c323ac2d8b10e15d7ecc304a026c85` |
| [`morphogenesis/experiments/L1_field/x89_f047_pattern_s267.json`](../morphogenesis/experiments/L1_field/x89_f047_pattern_s267.json) | other | 62440 | `52541d3cdc2de31e2b41561910617e8a85979a53ca2596407a907c837ada8723` |
| [`morphogenesis/experiments/L1_field/x89_f047_pattern_s268.json`](../morphogenesis/experiments/L1_field/x89_f047_pattern_s268.json) | other | 62442 | `ba23391dfc53e9190942389a4d4b67bc9509259015d414278c5fb5c02161c4d7` |
| [`morphogenesis/experiments/L1_field/x89_f048_pattern_s261.json`](../morphogenesis/experiments/L1_field/x89_f048_pattern_s261.json) | other | 61487 | `53ac96382e32b205e5f72d42f400d98950392e770dfb0c8e618264352afcfebe` |
| [`morphogenesis/experiments/L1_field/x89_f048_pattern_s262.json`](../morphogenesis/experiments/L1_field/x89_f048_pattern_s262.json) | other | 60818 | `d1bb84b6a442629bc331ef669ce53af017ec4da6ee3f6f2066920c10276ed454` |
| [`morphogenesis/experiments/L1_field/x89_f048_pattern_s263.json`](../morphogenesis/experiments/L1_field/x89_f048_pattern_s263.json) | other | 60805 | `60b69984b3867a3e73f64898cc54bef2f5f84e182b033ebfc81f3dd60b8f63e7` |
| [`morphogenesis/experiments/L1_field/x89_f048_pattern_s264.json`](../morphogenesis/experiments/L1_field/x89_f048_pattern_s264.json) | other | 61369 | `820e676e54f5b6eb65639a814845c4ce1daf50b516e1332797c5f455823e58c1` |
| [`morphogenesis/experiments/L1_field/x89_f048_pattern_s265.json`](../morphogenesis/experiments/L1_field/x89_f048_pattern_s265.json) | other | 61329 | `b4ef3009bd09acc81129c761eb5a4acfca5a276acc32608764a4c792e8ccd0e0` |
| [`morphogenesis/experiments/L1_field/x89_f048_pattern_s266.json`](../morphogenesis/experiments/L1_field/x89_f048_pattern_s266.json) | other | 61496 | `0793063862fc73452bc1729cc820007038134d56fc704619b5f25dd6164a4039` |
| [`morphogenesis/experiments/L1_field/x89_f048_pattern_s267.json`](../morphogenesis/experiments/L1_field/x89_f048_pattern_s267.json) | other | 61375 | `8a263efd6d8a1b65005475498ce9346e91b3b1d8165bc187038489d67340057a` |
| [`morphogenesis/experiments/L1_field/x89_f048_pattern_s268.json`](../morphogenesis/experiments/L1_field/x89_f048_pattern_s268.json) | other | 61364 | `b3df1b39e569a01440dfeb67ed1e8f97cabd838e570d92b1cd4ef640cd7f1027` |
| [`morphogenesis/experiments/L1_field/x89_f049_pattern_s261.json`](../morphogenesis/experiments/L1_field/x89_f049_pattern_s261.json) | other | 61491 | `102fe23fda452277267cd03f99536151dbea8be00487744942c0cd8845d88197` |
| [`morphogenesis/experiments/L1_field/x89_f049_pattern_s262.json`](../morphogenesis/experiments/L1_field/x89_f049_pattern_s262.json) | other | 60822 | `a65f21fe66cc9c80534de62f0e5d60960194e6a29eea58f3af458bf96487a5ff` |
| [`morphogenesis/experiments/L1_field/x89_f049_pattern_s263.json`](../morphogenesis/experiments/L1_field/x89_f049_pattern_s263.json) | other | 61368 | `59d3d6a1b1390d1335923d7aee301226314466b922a61463d55fbd34a74952a4` |
| [`morphogenesis/experiments/L1_field/x89_f049_pattern_s264.json`](../morphogenesis/experiments/L1_field/x89_f049_pattern_s264.json) | other | 60819 | `5d3d35d3fa9ab73a1b5b5874eb8c96be8080ba3f0cc7f3d2f43eae40f94100ba` |
| [`morphogenesis/experiments/L1_field/x89_f049_pattern_s265.json`](../morphogenesis/experiments/L1_field/x89_f049_pattern_s265.json) | other | 61353 | `e176ae874fcfa9758d4ee0f49c1c7b81b98f642b7bd4dcea8f46cd2fc5cce46a` |
| [`morphogenesis/experiments/L1_field/x89_f049_pattern_s266.json`](../morphogenesis/experiments/L1_field/x89_f049_pattern_s266.json) | other | 61489 | `5142b020dc62c8b73151abd81d00f2cd7b4ca3bdc6cd489c3168bc41172d29a1` |
| [`morphogenesis/experiments/L1_field/x89_f049_pattern_s267.json`](../morphogenesis/experiments/L1_field/x89_f049_pattern_s267.json) | other | 60821 | `c2d016a01ba271b417a414a8a9a8e18423fe70ae4a456120166d2744b52f9e61` |
| [`morphogenesis/experiments/L1_field/x89_f049_pattern_s268.json`](../morphogenesis/experiments/L1_field/x89_f049_pattern_s268.json) | other | 60822 | `1aa0d9312b9a308f2f830e16be0353bc913e9835590f6994361373e84999a8b7` |
| [`morphogenesis/experiments/L1_field/x89_series_index.json`](../morphogenesis/experiments/L1_field/x89_series_index.json) | other | 3194 | `173361d87edb9a6baef131519e89dea375e332a21dbf08b7880955f13aef5e7a` |
| [`morphogenesis/experiments/L1_field/x90_f048_pattern_s271.json`](../morphogenesis/experiments/L1_field/x90_f048_pattern_s271.json) | other | 118035 | `25123d23fd0e9fb73e93705e132cce70901b2db3b3801d0df7856889778c6d6c` |
| [`morphogenesis/experiments/L1_field/x90_f048_pattern_s272.json`](../morphogenesis/experiments/L1_field/x90_f048_pattern_s272.json) | other | 116871 | `b96766e109305bfa3402317da1aafc87988d8d27bebd1ad6a473e8fafdeef33b` |
| [`morphogenesis/experiments/L1_field/x90_f048_pattern_s273.json`](../morphogenesis/experiments/L1_field/x90_f048_pattern_s273.json) | other | 118302 | `bb462c0227d238ad2c7c7885df021afa0f5b3f20612ae27fba3f7b42de2d8ebe` |
| [`morphogenesis/experiments/L1_field/x90_f048_pattern_s274.json`](../morphogenesis/experiments/L1_field/x90_f048_pattern_s274.json) | other | 118281 | `3d0e7c915495608f88f8e5c0140e108ed3075d232d2f2446e652d2100610be70` |
| [`morphogenesis/experiments/L1_field/x90_f048_pattern_s275.json`](../morphogenesis/experiments/L1_field/x90_f048_pattern_s275.json) | other | 117863 | `928fbab1bd4e1c1834abec3c53f7082e4fdecc15756d005ae93be7377081092e` |
| [`morphogenesis/experiments/L1_field/x90_f048_pattern_s276.json`](../morphogenesis/experiments/L1_field/x90_f048_pattern_s276.json) | other | 118056 | `83339d6eba21c68bfac2cc5cf6b902b8559ee9fe840ec460f93dcc4840018b11` |
| [`morphogenesis/experiments/L1_field/x90_f048_pattern_s277.json`](../morphogenesis/experiments/L1_field/x90_f048_pattern_s277.json) | other | 117734 | `9551201c2e72c53bd6c25b4aaad6a96c1eb5e269774353a5980aeb777df4f31e` |
| [`morphogenesis/experiments/L1_field/x90_f048_pattern_s278.json`](../morphogenesis/experiments/L1_field/x90_f048_pattern_s278.json) | other | 116365 | `7357767fa73a737c647c1db6180b14aae1036c84f896c3859e4191bc670e481f` |
| [`morphogenesis/experiments/L1_field/x90_f049_pattern_s271.json`](../morphogenesis/experiments/L1_field/x90_f049_pattern_s271.json) | other | 118063 | `c506f65df756c4777501feb011263a78fc9fb70c489a0ff984948361e09c7edf` |
| [`morphogenesis/experiments/L1_field/x90_f049_pattern_s272.json`](../morphogenesis/experiments/L1_field/x90_f049_pattern_s272.json) | other | 116814 | `e1b52c11cb86baad1fa61491c9ef44e49d520da432e350eb40a850b77cbdfa9b` |
| [`morphogenesis/experiments/L1_field/x90_f049_pattern_s273.json`](../morphogenesis/experiments/L1_field/x90_f049_pattern_s273.json) | other | 118079 | `0411570308ccee8224e3ac863c3d13189993ff5f9ba9dad294c6a487bfaa1cb3` |
| [`morphogenesis/experiments/L1_field/x90_f049_pattern_s274.json`](../morphogenesis/experiments/L1_field/x90_f049_pattern_s274.json) | other | 117753 | `9ef5c601b63f77e5587db8da82b9312bbfed2f1d9e1c81ab7922e13e14e82fbb` |
| [`morphogenesis/experiments/L1_field/x90_f049_pattern_s275.json`](../morphogenesis/experiments/L1_field/x90_f049_pattern_s275.json) | other | 117358 | `c5abee47ac0b6ed1e969400d3cfaa241c3f520f5053efc9f29a372a5dccb2b16` |
| [`morphogenesis/experiments/L1_field/x90_f049_pattern_s276.json`](../morphogenesis/experiments/L1_field/x90_f049_pattern_s276.json) | other | 118065 | `37dbe0b19285f89e73db4753d25f9deb1b52e92f87ebf90c49cecac8e5f724fb` |
| [`morphogenesis/experiments/L1_field/x90_f049_pattern_s277.json`](../morphogenesis/experiments/L1_field/x90_f049_pattern_s277.json) | other | 117776 | `d0a5f76d6a9c40de61db25e329f1edacc7fb9e6dd9fa69f2bab436f781bcf2dc` |
| [`morphogenesis/experiments/L1_field/x90_f049_pattern_s278.json`](../morphogenesis/experiments/L1_field/x90_f049_pattern_s278.json) | other | 116405 | `8ec1d2016749bbfbc363250040ded6a08be13300ffa25297cc1e6d9145657345` |
| [`morphogenesis/experiments/L1_field/x90_f050_pattern_s271.json`](../morphogenesis/experiments/L1_field/x90_f050_pattern_s271.json) | other | 117920 | `1fa6520c4de6be9b2dadf775ecb825897fafd00de56cae9b5a68956d49e618a9` |
| [`morphogenesis/experiments/L1_field/x90_f050_pattern_s272.json`](../morphogenesis/experiments/L1_field/x90_f050_pattern_s272.json) | other | 116830 | `582fa921c78f99a461a5666788b08ef8059b0048688aaf169a0078c85df44fdf` |
| [`morphogenesis/experiments/L1_field/x90_f050_pattern_s273.json`](../morphogenesis/experiments/L1_field/x90_f050_pattern_s273.json) | other | 117892 | `f696163052c56eb8ee4c0e8d05dd9b35165d22bed258073ae56602534a511553` |
| [`morphogenesis/experiments/L1_field/x90_f050_pattern_s274.json`](../morphogenesis/experiments/L1_field/x90_f050_pattern_s274.json) | other | 117368 | `a7c10544b3d49d286798571ea2486f279c2a5cac13c31316f8822015ac98c3d6` |
| [`morphogenesis/experiments/L1_field/x90_f050_pattern_s275.json`](../morphogenesis/experiments/L1_field/x90_f050_pattern_s275.json) | other | 117362 | `1935ca6112251d313401e25859d94b96c3ffd76707a1718903f8ad6c7d493fb5` |
| [`morphogenesis/experiments/L1_field/x90_f050_pattern_s276.json`](../morphogenesis/experiments/L1_field/x90_f050_pattern_s276.json) | other | 117912 | `73dc8d57d06157e12d751996aa7762ec4a507665f69dbab828f04f19141a45de` |
| [`morphogenesis/experiments/L1_field/x90_f050_pattern_s277.json`](../morphogenesis/experiments/L1_field/x90_f050_pattern_s277.json) | other | 117252 | `efc6e7682170caa05e767530f1f353a338434367e0a3ba691a2ba6828c1b6bc9` |
| [`morphogenesis/experiments/L1_field/x90_f050_pattern_s278.json`](../morphogenesis/experiments/L1_field/x90_f050_pattern_s278.json) | other | 116371 | `a409d449c47c05d2c9381183bee7e9399e397ff0e41a55f009eef9f7edcb917d` |
| [`morphogenesis/experiments/L1_field/x90_series_index.json`](../morphogenesis/experiments/L1_field/x90_series_index.json) | other | 2425 | `1c7cbd9c58b49ccfda51be606d22f9f832090bcffff6634a642b413e6edf53ac` |
| [`morphogenesis/experiments/L1_field/x96bpilot_dw008_g005.json`](../morphogenesis/experiments/L1_field/x96bpilot_dw008_g005.json) | other | 464468 | `dff1ea552172e1b9466268d2e98fc075ba274483441f4e282fe6aba3d02a2d99` |
| [`morphogenesis/experiments/L1_field/x96bpilot_dw008_g01.json`](../morphogenesis/experiments/L1_field/x96bpilot_dw008_g01.json) | other | 538421 | `0f5e4c39e43aa177262e687e067b8040d5bd8d490e2f8b32dda80ef6d5ea5892` |
| [`morphogenesis/experiments/L1_field/x96bpilot_dw008_g02.json`](../morphogenesis/experiments/L1_field/x96bpilot_dw008_g02.json) | other | 151249 | `e22ba5352223c3350755fa4e6bb4d1ce88c0693f649d553ba878e08d8fb1fa3c` |
| [`morphogenesis/experiments/L1_field/x96bpilot_dw016_g005.json`](../morphogenesis/experiments/L1_field/x96bpilot_dw016_g005.json) | other | 688054 | `281c3af4b86a1394610555fe714905bcbc3007ddb32f6e700c51402bb73c57fa` |
| [`morphogenesis/experiments/L1_field/x96bpilot_dw016_g01.json`](../morphogenesis/experiments/L1_field/x96bpilot_dw016_g01.json) | other | 547629 | `2792977c705a822f57d8b734c993ccaadd5eb1d45d9357d5a143011a6300d83c` |
| [`morphogenesis/experiments/L1_field/x96bpilot_dw016_g02.json`](../morphogenesis/experiments/L1_field/x96bpilot_dw016_g02.json) | other | 205341 | `b4e7323897c7a3b39257819cf36dac7fda48b4ba86a6268e049067732c5a40ad` |
| [`morphogenesis/experiments/L1_field/x96bpilot_dw032_g005.json`](../morphogenesis/experiments/L1_field/x96bpilot_dw032_g005.json) | other | 452533 | `c2cef604b120c5591c50d9aad0f64c5ff3670b0b8a65abae3099fc1bec3329d7` |
| [`morphogenesis/experiments/L1_field/x96bpilot_dw032_g01.json`](../morphogenesis/experiments/L1_field/x96bpilot_dw032_g01.json) | other | 320892 | `ecf344821209b271ac982150ca4feda8d41f45e3bfd76722f89efb1ce2e19c79` |
| [`morphogenesis/experiments/L1_field/x96bpilot_dw032_g02.json`](../morphogenesis/experiments/L1_field/x96bpilot_dw032_g02.json) | other | 60937 | `6b0ce366edd8df1c8b9d89da439d03532d837808a512ebe527f6fc47d11c19a6` |
| [`morphogenesis/experiments/L1_field/x96bpilot_index.json`](../morphogenesis/experiments/L1_field/x96bpilot_index.json) | other | 4637 | `04ed0134954a57cb72103a60a86961133101900356282cbf1bf6f7c6cd6bb93e` |
| [`morphogenesis/experiments/L1_field/x96bpilot_w_off.json`](../morphogenesis/experiments/L1_field/x96bpilot_w_off.json) | other | 927799 | `924522b50c6bc8ce8c26a0ec0bd40d28c60b1bc6da452780a96783fb753e6be2` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw008_s411.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw008_s411.compact.json) | other | 77264 | `8adb3f24209d8eec85ad796b15b95fe1ac055b794e1e8a70c567968cba3f5dc6` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw008_s412.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw008_s412.compact.json) | other | 98354 | `1f8a583b90e235780e58f8bc4ef38dbc0c3dc860db0b0e757b6a87d9c360a4d3` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw008_s413.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw008_s413.compact.json) | other | 100417 | `3e04b979e9bbc515d207c0c0d640886e12b015dc679efbd8f770a4631224d7bc` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw016_s411.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw016_s411.compact.json) | other | 91080 | `4df03ee6b629602bd4cc8c86e651ab0c8ddc603bb434b9fcf833b52798a5fe22` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw016_s412.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw016_s412.compact.json) | other | 102196 | `1b2cf90cc57403a2c062f61c52c64e02a508e397569d565d3445988a469d92a0` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw016_s413.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw016_s413.compact.json) | other | 95606 | `482035928551f2c7c1bcbed8e30e72252513acc2f3b816ed549cf8d76dc14bce` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw032_s411.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw032_s411.compact.json) | other | 64477 | `1720bd100fe92f232f1a3d58e7b9492d359a10b2e24ee85a70d05e8b528f46b0` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw032_s412.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw032_s412.compact.json) | other | 65495 | `4c01242c72ac5c2ea457059dac2b6bbf90e9381ada085af23d805587ddd96aec` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw032_s413.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw032_s413.compact.json) | other | 63499 | `33f2a282acf4e126339d6d76007d506a44baa8be1b26dc71bcd8f0afb17572dd` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw064_s411.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw064_s411.compact.json) | other | 62952 | `2d1293e02abdfd883f9192273cb51d11a923ffaca9b7baaf7af0496b4f1cd2fa` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw064_s412.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw064_s412.compact.json) | other | 63113 | `f770b671fbbe07eee56d7b5052099dc35cac8db2bebfae36ab894fcd672cfa92` |
| [`morphogenesis/experiments/L1_field/x96d_f030_dw064_s413.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_dw064_s413.compact.json) | other | 59196 | `ac79bf4cc33a522cb2299bc57f6d3d759ae946c3ed3b7536d2e32df9d1ea7d46` |
| [`morphogenesis/experiments/L1_field/x96d_f030_s411.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_s411.compact.json) | other | 107697 | `18519ce445c8a66b154b099a1c5d7c5bb02447625bfdd6b41d34855987e505cf` |
| [`morphogenesis/experiments/L1_field/x96d_f030_s412.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_s412.compact.json) | other | 105877 | `ce6470345f6b3cb3758b2168afc923061fadf8154435a0d9ccd519b11d99e67d` |
| [`morphogenesis/experiments/L1_field/x96d_f030_s413.compact.json`](../morphogenesis/experiments/L1_field/x96d_f030_s413.compact.json) | other | 107667 | `96e74c5b75da35580ed49fc937dad3b18fb860fd38b77dcbf7d3be17820719c8` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw008_s411.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw008_s411.compact.json) | other | 30220 | `c59f28747369f522eeffc92beb25f772c7d80487604dbe99fe243c7093ac3e20` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw008_s412.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw008_s412.compact.json) | other | 25860 | `4425a24aacee5a175edeb22c022a253296dd86712a90b0df58e963aeb7eb1754` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw008_s413.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw008_s413.compact.json) | other | 31164 | `fbf75f4a1562f6bb1711e6dde08d5a68a5ac36702631e1bcd1a9bc6e39ac2642` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw016_s411.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw016_s411.compact.json) | other | 28455 | `6af97cd578f1ec17f8f7c941b7d65f2a282d4d5508d6929fc8e9c89321f2a15a` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw016_s412.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw016_s412.compact.json) | other | 28695 | `568361c83bd87eea1ccbf2aa640e9b99f669707a2f1ebed03f16e7fc5b59b08d` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw016_s413.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw016_s413.compact.json) | other | 40183 | `5d312bb5eb8f246daf024e940b388939afb53ab93e120a7a0cd0e7bb43de20df` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw032_s411.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw032_s411.compact.json) | other | 24093 | `43ae18669b9fa8d418a46e0cbf0cbf91ea35137f50e62ab5605a2d0f6641160c` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw032_s412.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw032_s412.compact.json) | other | 30365 | `7157db9988533c6c4621810990535cc86e03816fd8b55552dae90ddb95718996` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw032_s413.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw032_s413.compact.json) | other | 22603 | `3d2f67764e743d8e65637af77b4689e4c5cdffe43e7af1e0b12329aa83203110` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw064_s411.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw064_s411.compact.json) | other | 24146 | `5037c1415e10a2f9ea8708866b011ddc7c0820d93b2a6312cad53c2b0bcd16ea` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw064_s412.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw064_s412.compact.json) | other | 31665 | `fb8de8b72a42f03ae707f0d6c7b77a947de6122e4bcf86b7ae78aff0c0d042ea` |
| [`morphogenesis/experiments/L1_field/x96d_f040_dw064_s413.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_dw064_s413.compact.json) | other | 23485 | `80a98e931021c127175a2072c3c6b67a6ba8397b6065275a7faa2ec8b478cbfb` |
| [`morphogenesis/experiments/L1_field/x96d_f040_s411.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_s411.compact.json) | other | 22254 | `94154b0863ee1bfe39faf6c8f019e40aae7950fa8d2c248bd520284f4c7e93aa` |
| [`morphogenesis/experiments/L1_field/x96d_f040_s412.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_s412.compact.json) | other | 19370 | `15df2a0dbb456baf5cb5fc8e9deef14dd39b1ea645cbd20fdc3927b6b3d98a43` |
| [`morphogenesis/experiments/L1_field/x96d_f040_s413.compact.json`](../morphogenesis/experiments/L1_field/x96d_f040_s413.compact.json) | other | 16925 | `034e4a9b6c0a0ef06395d489786b717a2a9261705ce93dcb2a1088b2fab40edf` |
| [`morphogenesis/experiments/L1_field/x96d_series_index.json`](../morphogenesis/experiments/L1_field/x96d_series_index.json) | other | 12796 | `eaac5b9fa292d3b732dc6f612ab616537cb02b53c29789209400c651cdec256d` |
| [`morphogenesis/experiments/L1_field/x96pilot_dw008_g05.json`](../morphogenesis/experiments/L1_field/x96pilot_dw008_g05.json) | other | 60555 | `ddc300915093f0c769d24a050ddd2988e3577455dcc20ced02cd39764dd16c75` |
| [`morphogenesis/experiments/L1_field/x96pilot_dw008_g15.json`](../morphogenesis/experiments/L1_field/x96pilot_dw008_g15.json) | other | 41435 | `60acbcfd68bdbe03e01d2d44ef5afe66583d461246fcb07d1b9f004174d61340` |
| [`morphogenesis/experiments/L1_field/x96pilot_dw016_g05.json`](../morphogenesis/experiments/L1_field/x96pilot_dw016_g05.json) | other | 60554 | `0c0ba1c92c34decac58003eaf1cb049c4234ff9e1cfdf2895428f9971aa1ee9f` |
| [`morphogenesis/experiments/L1_field/x96pilot_dw016_g15.json`](../morphogenesis/experiments/L1_field/x96pilot_dw016_g15.json) | other | 41435 | `82035380b2c78955bea1e4161b37515a18b574dc6dd47a9b2a9c41e30d38d7cb` |
| [`morphogenesis/experiments/L1_field/x96pilot_dw032_g05.json`](../morphogenesis/experiments/L1_field/x96pilot_dw032_g05.json) | other | 41821 | `6135e244b4fca61817e7d513c53da3606b2341597e4efc29688042a8cfabfaa1` |
| [`morphogenesis/experiments/L1_field/x96pilot_dw032_g15.json`](../morphogenesis/experiments/L1_field/x96pilot_dw032_g15.json) | other | 41435 | `bdff0a2ee844f2e3d52db02a25e21c9c3bbc6861ba23731455b3687e4a8ec454` |
| [`morphogenesis/experiments/L1_field/x96pilot_index.json`](../morphogenesis/experiments/L1_field/x96pilot_index.json) | other | 3194 | `4beea8769a4ac204f6b56bb2fe9cc77414ebb0c5a4510f6a0a59208c1f2c4794` |
| [`morphogenesis/experiments/L1_field/x96pilot_w_off.json`](../morphogenesis/experiments/L1_field/x96pilot_w_off.json) | other | 927796 | `927528e9440b6e8c9b8e3dae04a2d4d4ec380300e8418c4b1459879f74aa2567` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr015_s281.json`](../morphogenesis/experiments/L1_field/x99_f030_thr015_s281.json) | other | 866601 | `1892855f168d5d3a304e2682af723ea3981afddbbff5e9a399f2b23a4261e8f7` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr015_s282.json`](../morphogenesis/experiments/L1_field/x99_f030_thr015_s282.json) | other | 868622 | `5c8cfb9023cc3124d386e3de720bafb9ef94189bb2e19c3c9103c6f1f3ae3f8d` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr015_s283.json`](../morphogenesis/experiments/L1_field/x99_f030_thr015_s283.json) | other | 911562 | `96d2ab1463cf99b9119188d2efc17a7e44c02f0119a3fd814038a75566ee0bd2` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr015_s284.json`](../morphogenesis/experiments/L1_field/x99_f030_thr015_s284.json) | other | 858965 | `2b06a105cf61b0d753e10cf750fd7b14d27e3c64423e77864b6b738c2df6e2bc` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr015_s285.json`](../morphogenesis/experiments/L1_field/x99_f030_thr015_s285.json) | other | 849778 | `83570e7b4ef64976df314d670300128df6da04eb072737a747399974874a052c` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr015_s286.json`](../morphogenesis/experiments/L1_field/x99_f030_thr015_s286.json) | other | 725907 | `666413d686dc58a770c605ceb19c53cb396f6a46a726e1e3f3b53bb9141f0855` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr015_s287.json`](../morphogenesis/experiments/L1_field/x99_f030_thr015_s287.json) | other | 740096 | `2404fe417195a221864b11180ae98708f09adcfab92f7bdffdd880bc6c2dbf0d` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr015_s288.json`](../morphogenesis/experiments/L1_field/x99_f030_thr015_s288.json) | other | 929170 | `e569775ad1132ac6bb927c54818b1a8a22642ab036463f4363b8f050e59a15a1` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr015_s289.json`](../morphogenesis/experiments/L1_field/x99_f030_thr015_s289.json) | other | 746206 | `c3ff68970bc7189e73bbc38faaa9d40bfe646a5d0644d98d4e96e5f55af0e830` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr015_s290.json`](../morphogenesis/experiments/L1_field/x99_f030_thr015_s290.json) | other | 975779 | `e779f60521dab995c670a2367446165512909b0be171843af673181710c64298` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr025_s281.json`](../morphogenesis/experiments/L1_field/x99_f030_thr025_s281.json) | other | 1113636 | `27b548e5e91140f3963d6377339eb216257c2a4c149c7fa676a9af840353be00` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr025_s282.json`](../morphogenesis/experiments/L1_field/x99_f030_thr025_s282.json) | other | 1126948 | `f36d40f554a534e96346b4a20f41f374e2dc0ec9d0e80388d3d6b01a6750d374` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr025_s283.json`](../morphogenesis/experiments/L1_field/x99_f030_thr025_s283.json) | other | 1057415 | `0bf295fb71434e7de89804f9c4adc841c9eee48aa900ff52e894f7b62c27fd7d` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr025_s284.json`](../morphogenesis/experiments/L1_field/x99_f030_thr025_s284.json) | other | 1099744 | `663f33bfe4d0c4332eee607a6a4f28c194938f1a0e81d170874c2a3c65827671` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr025_s285.json`](../morphogenesis/experiments/L1_field/x99_f030_thr025_s285.json) | other | 1057681 | `7dabd7403b4fcec224c42ad762b324cad6e7a86fb6e927f18e3b6b9c846fc013` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr025_s286.json`](../morphogenesis/experiments/L1_field/x99_f030_thr025_s286.json) | other | 945176 | `812bc5bfd4a1d5be3c5c419eb21172db0f249c4c41b9ce1aa2c2a1d7ea3822cd` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr025_s287.json`](../morphogenesis/experiments/L1_field/x99_f030_thr025_s287.json) | other | 968605 | `d76ce9940df7e1c31a831b49aa4e7c113e0d26209928138f069ecfca5496cf34` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr025_s288.json`](../morphogenesis/experiments/L1_field/x99_f030_thr025_s288.json) | other | 1112803 | `8a4666c2adbf68acacd365f570d57441b7f8ecc20d414efd37b8291e789cee3b` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr025_s289.json`](../morphogenesis/experiments/L1_field/x99_f030_thr025_s289.json) | other | 1056939 | `3584515c4a9b59bb229dd6510ee5df0b425c5554fb6deb5c9bec1f1fc9be6af4` |
| [`morphogenesis/experiments/L1_field/x99_f030_thr025_s290.json`](../morphogenesis/experiments/L1_field/x99_f030_thr025_s290.json) | other | 1121348 | `7f89a68cb92a61cb625f72758ae1c99886cd4a91051e0f6c9c66839f5d73d44a` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr015_s281.json`](../morphogenesis/experiments/L1_field/x99_f040_thr015_s281.json) | other | 103730 | `ac9ed208133d674b24f7bfba32a5a931fc53082c45ed55e70c9ff77a200d4995` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr015_s282.json`](../morphogenesis/experiments/L1_field/x99_f040_thr015_s282.json) | other | 101065 | `7f89199095ae2343c09279f378cee555a5abda198e08ba5f7a45d3b34b717baf` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr015_s283.json`](../morphogenesis/experiments/L1_field/x99_f040_thr015_s283.json) | other | 93085 | `1b012d0275e366711c5bc273538e5ce341033667416100c8951f42782dc7d568` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr015_s284.json`](../morphogenesis/experiments/L1_field/x99_f040_thr015_s284.json) | other | 84878 | `e62762778cc55136ee88ea43ad1a00e237d44193c4b1ab58a8915eac36d06c14` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr015_s285.json`](../morphogenesis/experiments/L1_field/x99_f040_thr015_s285.json) | other | 95000 | `3573c276b171055694ae244a0854d3ce7250edab622391be082ddb974bbfaa97` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr015_s286.json`](../morphogenesis/experiments/L1_field/x99_f040_thr015_s286.json) | other | 134382 | `70b82f2f2a65db783c4d87e561530c9fc21f7dcbe9cebb74405487d3dc20e26e` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr015_s287.json`](../morphogenesis/experiments/L1_field/x99_f040_thr015_s287.json) | other | 95558 | `96dd27dca9eb0d889c115a4b7b2b0018a55ec997b0fb08f29df3dc2823b0f8cd` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr015_s288.json`](../morphogenesis/experiments/L1_field/x99_f040_thr015_s288.json) | other | 86390 | `fb2c10ae7e034d16ecdc4687ffcf9274ac63e6e13a89616e158c5383917ab238` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr015_s289.json`](../morphogenesis/experiments/L1_field/x99_f040_thr015_s289.json) | other | 115496 | `884eca68b120358419024a7e0a46591a6d13228c9a3d98c6f4516267843ab2a0` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr015_s290.json`](../morphogenesis/experiments/L1_field/x99_f040_thr015_s290.json) | other | 135176 | `27e0e3d0ab72722f0a9eda900c265b29bc0058a0345b642451d7a7a21e261fc9` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr025_s281.json`](../morphogenesis/experiments/L1_field/x99_f040_thr025_s281.json) | other | 496538 | `32738c00d78b4e9901dac44140163b6b70d473076eb0192fad64f925488421e2` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr025_s282.json`](../morphogenesis/experiments/L1_field/x99_f040_thr025_s282.json) | other | 454946 | `8b5b81fdd008cb832de7462b0f5f2ffe62481fb95539a6f3642890e295733695` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr025_s283.json`](../morphogenesis/experiments/L1_field/x99_f040_thr025_s283.json) | other | 574724 | `cb24954d64a2e2ed0241bc4a724fe43d2a7948eeef91643462180c36bf56bb69` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr025_s284.json`](../morphogenesis/experiments/L1_field/x99_f040_thr025_s284.json) | other | 395225 | `5d8651f62fa475ed29db83344d41f0403832c62cc1a77065e82591d18936cbcb` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr025_s285.json`](../morphogenesis/experiments/L1_field/x99_f040_thr025_s285.json) | other | 383726 | `276727fbf9e7f19c962bfced3d8d9a340e73b472da8e966a025eb37f30fda56c` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr025_s286.json`](../morphogenesis/experiments/L1_field/x99_f040_thr025_s286.json) | other | 577244 | `55093fdcb773b99b35d63facd04b4670db48a93a06b00108881b17bfd412b8d3` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr025_s287.json`](../morphogenesis/experiments/L1_field/x99_f040_thr025_s287.json) | other | 547874 | `099971cb8d265dc359b97762a0e8874a70253e8978577fee3a7603ace501eaf6` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr025_s288.json`](../morphogenesis/experiments/L1_field/x99_f040_thr025_s288.json) | other | 572632 | `0e651012c47f04cd4c756a2bacce145c22b3dd03b0ded0ea6156f386c43f08bf` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr025_s289.json`](../morphogenesis/experiments/L1_field/x99_f040_thr025_s289.json) | other | 582972 | `5eae7d283ef4448d6a77ecd51e36dd5f244d879c352da0dd9132e865506f9ccb` |
| [`morphogenesis/experiments/L1_field/x99_f040_thr025_s290.json`](../morphogenesis/experiments/L1_field/x99_f040_thr025_s290.json) | other | 553106 | `8138afb31e47c83d7ac66f4b864519f0ae409c43ea52095464fe6205cde8476a` |
| [`morphogenesis/experiments/L1_field/x99_series_index.json`](../morphogenesis/experiments/L1_field/x99_series_index.json) | other | 4266 | `831984768f6134add73a2d3872b49af5e4579824c65938722eb21577d04d0699` |
| [`morphogenesis/experiments/R1_replicator/pilot/r1_pilot_k1_seed1.json`](../morphogenesis/experiments/R1_replicator/pilot/r1_pilot_k1_seed1.json) | other | 1465 | `b8a589e57a0916def23cace3d03d09b089a2981d073cf7c24680b2bdb17182ab` |
| [`morphogenesis/experiments/R1_replicator/pilot/r1_pilot_k2_seed1.json`](../morphogenesis/experiments/R1_replicator/pilot/r1_pilot_k2_seed1.json) | other | 1510 | `630aa11912f500ef99d3131bb68d183ec856f2706828c150091f2b9369dbd0f7` |
| [`morphogenesis/experiments/R1_replicator/pilot/r1_pilot_k8_seed1.json`](../morphogenesis/experiments/R1_replicator/pilot/r1_pilot_k8_seed1.json) | other | 1477 | `f14452b3b86142186cee4abd83d6819d1491262cd0f880ec5697c9b249c832e4` |
| [`morphogenesis/experiments/R1_replicator/r1_k1_seed1.json`](../morphogenesis/experiments/R1_replicator/r1_k1_seed1.json) | other | 1465 | `b8a589e57a0916def23cace3d03d09b089a2981d073cf7c24680b2bdb17182ab` |
| [`morphogenesis/experiments/R1_replicator/r1_k1_seed10.json`](../morphogenesis/experiments/R1_replicator/r1_k1_seed10.json) | other | 1406 | `6cfa4e5dea3b0fddd74670f6573e4d87f79358a5afb26bbbe63203f5b896ddf2` |
| [`morphogenesis/experiments/R1_replicator/r1_k1_seed2.json`](../morphogenesis/experiments/R1_replicator/r1_k1_seed2.json) | other | 1299 | `fdfa3591939f5fe47b0a6594cfc3cc334c1e5233707fa2f7580d3582b4f863dd` |
| [`morphogenesis/experiments/R1_replicator/r1_k1_seed3.json`](../morphogenesis/experiments/R1_replicator/r1_k1_seed3.json) | other | 1315 | `ebd97e80eb1e2459ce1b2e0c679e770407a9d1ae7782e70f0b08e533edea569f` |
| [`morphogenesis/experiments/R1_replicator/r1_k1_seed4.json`](../morphogenesis/experiments/R1_replicator/r1_k1_seed4.json) | other | 1465 | `eb21c6173405e001b64cd1f2ee0c95aa79bfa3fd1e7a3b4c08dc165f22e33d02` |
| [`morphogenesis/experiments/R1_replicator/r1_k1_seed5.json`](../morphogenesis/experiments/R1_replicator/r1_k1_seed5.json) | other | 1434 | `2817cbcd9779059f52dcb904dde9c16baa715c059a2dda2234db7eac741ffa45` |
| [`morphogenesis/experiments/R1_replicator/r1_k1_seed6.json`](../morphogenesis/experiments/R1_replicator/r1_k1_seed6.json) | other | 1444 | `aa9e240985967c2c4d34717aa95bed789529ac7146f101b38a9310b605cfa4f4` |
| [`morphogenesis/experiments/R1_replicator/r1_k1_seed7.json`](../morphogenesis/experiments/R1_replicator/r1_k1_seed7.json) | other | 1441 | `4a069dfb42521b523f7467968fef1b8d91ee7d0d7da798a87c1f916bc556ca09` |
| [`morphogenesis/experiments/R1_replicator/r1_k1_seed8.json`](../morphogenesis/experiments/R1_replicator/r1_k1_seed8.json) | other | 1500 | `514661ffa6675ac415d2dac24a446198992add8a34f29d0fec551b7f89124715` |
| [`morphogenesis/experiments/R1_replicator/r1_k1_seed9.json`](../morphogenesis/experiments/R1_replicator/r1_k1_seed9.json) | other | 1432 | `41c7258980d62e3164d6fa1d80b4ab3cca139937ae250081abcc8f4b5c09c782` |
| [`morphogenesis/experiments/R1_replicator/r1_k2_seed1.json`](../morphogenesis/experiments/R1_replicator/r1_k2_seed1.json) | other | 1510 | `630aa11912f500ef99d3131bb68d183ec856f2706828c150091f2b9369dbd0f7` |
| [`morphogenesis/experiments/R1_replicator/r1_k2_seed10.json`](../morphogenesis/experiments/R1_replicator/r1_k2_seed10.json) | other | 1475 | `c793316b8f8190c4e0c950f2bc083b69e0c0dcfdae4be67bd8a86000bcd5684d` |
| [`morphogenesis/experiments/R1_replicator/r1_k2_seed2.json`](../morphogenesis/experiments/R1_replicator/r1_k2_seed2.json) | other | 1429 | `4d55749c7cacb7340c7cd4702dc4715120be56ebe5d921b21e103592319f0ca3` |
| [`morphogenesis/experiments/R1_replicator/r1_k2_seed3.json`](../morphogenesis/experiments/R1_replicator/r1_k2_seed3.json) | other | 1475 | `4198f81be49ece75e45e46616882bd385147d66903fd59f04c5094f98fadbc3f` |
| [`morphogenesis/experiments/R1_replicator/r1_k2_seed4.json`](../morphogenesis/experiments/R1_replicator/r1_k2_seed4.json) | other | 1491 | `789f940324884931d99f216350af4f22d0a189e07531fa115a1e3ea8eee20f08` |
| [`morphogenesis/experiments/R1_replicator/r1_k2_seed5.json`](../morphogenesis/experiments/R1_replicator/r1_k2_seed5.json) | other | 1490 | `7fec11c3e65016693eacff8c810cfb62f04c0ade1e8e9ec1c94fc4fd06e7f9a7` |
| [`morphogenesis/experiments/R1_replicator/r1_k2_seed6.json`](../morphogenesis/experiments/R1_replicator/r1_k2_seed6.json) | other | 1527 | `b3962ae14a4d3f845878c401a7084643e1ae6b35f93ed2a2fa53911a8995e21c` |
| [`morphogenesis/experiments/R1_replicator/r1_k2_seed7.json`](../morphogenesis/experiments/R1_replicator/r1_k2_seed7.json) | other | 1532 | `b4f69d5ab8eddbf2686d5c7d70587e53a4032d2d534af5cf5a602711b9b75b5e` |
| [`morphogenesis/experiments/R1_replicator/r1_k2_seed8.json`](../morphogenesis/experiments/R1_replicator/r1_k2_seed8.json) | other | 1538 | `ee0ec722fc062074dbffe7513b22b2a3bc03c13a99e3ab3cc841dfa0805d9b21` |
| [`morphogenesis/experiments/R1_replicator/r1_k2_seed9.json`](../morphogenesis/experiments/R1_replicator/r1_k2_seed9.json) | other | 1491 | `6c7ccfe7fc9ae2457542babd397543789c8c3136e7bdddf2ae920f04d8d9b030` |
| [`morphogenesis/experiments/R1_replicator/r1_k8_seed1.json`](../morphogenesis/experiments/R1_replicator/r1_k8_seed1.json) | other | 1477 | `f14452b3b86142186cee4abd83d6819d1491262cd0f880ec5697c9b249c832e4` |
| [`morphogenesis/experiments/R1_replicator/r1_k8_seed10.json`](../morphogenesis/experiments/R1_replicator/r1_k8_seed10.json) | other | 1451 | `c2af673065288c8af9290b4ecdf7ea522f31e88a1c81d766760108b25c7911ca` |
| [`morphogenesis/experiments/R1_replicator/r1_k8_seed2.json`](../morphogenesis/experiments/R1_replicator/r1_k8_seed2.json) | other | 1433 | `535cb03166944006f5ecfa27f84c8de1bbeae360df37c2947be44a8b4aca15c5` |
| [`morphogenesis/experiments/R1_replicator/r1_k8_seed3.json`](../morphogenesis/experiments/R1_replicator/r1_k8_seed3.json) | other | 1464 | `cdca028a06ff2b6d43cb0d74eb8d4c3909c54b7e6f1a89e11402b073b17baa45` |
| [`morphogenesis/experiments/R1_replicator/r1_k8_seed4.json`](../morphogenesis/experiments/R1_replicator/r1_k8_seed4.json) | other | 1456 | `a7da78ce1c87b51d970f20f93c0ecb3b4b8c7db65fecce9e49c7bb0abf7de67b` |
| [`morphogenesis/experiments/R1_replicator/r1_k8_seed5.json`](../morphogenesis/experiments/R1_replicator/r1_k8_seed5.json) | other | 1447 | `57923be4c270bbe6dc4576cdf45217035a56c301f55b6b953a8ff18a663c9f63` |
| [`morphogenesis/experiments/R1_replicator/r1_k8_seed6.json`](../morphogenesis/experiments/R1_replicator/r1_k8_seed6.json) | other | 1475 | `f7764efd404c14772f3c2bcfef02fdb13b730bea8ff7d0c483efa405cbc3bc2b` |
| [`morphogenesis/experiments/R1_replicator/r1_k8_seed7.json`](../morphogenesis/experiments/R1_replicator/r1_k8_seed7.json) | other | 1478 | `375f8d76242bb442e19597f3f2cdc52046161de4ccbb17e0e18612ac02ac79c2` |
| [`morphogenesis/experiments/R1_replicator/r1_k8_seed8.json`](../morphogenesis/experiments/R1_replicator/r1_k8_seed8.json) | other | 1483 | `e0a5222405fc90e3327da1dd11e96d8641c9d43857210b513066fa3d6c31150a` |
| [`morphogenesis/experiments/R1_replicator/r1_k8_seed9.json`](../morphogenesis/experiments/R1_replicator/r1_k8_seed9.json) | other | 1461 | `fcb4debf72c5c9adb351b5482d96a491a2029a4dd6574aa206ca725d4c091ab4` |
| [`morphogenesis/experiments/R1_replicator/r1_matrix.json`](../morphogenesis/experiments/R1_replicator/r1_matrix.json) | other | 14811 | `efef07cc4c35f04b239416632e75aa19e0edbd320e9e2f193cf82d059fc72de8` |
| [`morphogenesis/experiments/R1_replicator/r1cap10_k1_seed1.json`](../morphogenesis/experiments/R1_replicator/r1cap10_k1_seed1.json) | other | 1563 | `6751a5d891b948e7cfd8eba6287a7b4a099f9e7741368f887c0ffc44017ae61f` |
| [`morphogenesis/experiments/R1_replicator/r1cap10_k1_seed10.json`](../morphogenesis/experiments/R1_replicator/r1cap10_k1_seed10.json) | other | 1477 | `6a7c18a7e4bea2ecd29c4ded1145970c32e1016c7d9412128b8d73cda188c7a0` |
| [`morphogenesis/experiments/R1_replicator/r1cap10_k1_seed2.json`](../morphogenesis/experiments/R1_replicator/r1cap10_k1_seed2.json) | other | 1383 | `0ee8b3f677a531b6e27d28cde2a0456ad62b2b073f73c4789c78588d350923d2` |
| [`morphogenesis/experiments/R1_replicator/r1cap10_k1_seed3.json`](../morphogenesis/experiments/R1_replicator/r1cap10_k1_seed3.json) | other | 1385 | `a6c59ac25979e7720266b0123e17affb8f656b3d278087041323e9525b00136c` |
| [`morphogenesis/experiments/R1_replicator/r1cap10_k1_seed4.json`](../morphogenesis/experiments/R1_replicator/r1cap10_k1_seed4.json) | other | 1545 | `6ac9057b2c714908c612d5900d95444a3f1bbd32ad8ad0dd38d9d14909724465` |
| [`morphogenesis/experiments/R1_replicator/r1cap10_k1_seed5.json`](../morphogenesis/experiments/R1_replicator/r1cap10_k1_seed5.json) | other | 1522 | `0667a428c951b645d2842a3cb8b1e14786369f2c517527ccbec70c29e4dc6b37` |
| [`morphogenesis/experiments/R1_replicator/r1cap10_k1_seed6.json`](../morphogenesis/experiments/R1_replicator/r1cap10_k1_seed6.json) | other | 1516 | `f1a1e69da12e588163d9a12c60eb8fa13bd4f42484591b95799a7def4503e11c` |
| [`morphogenesis/experiments/R1_replicator/r1cap10_k1_seed7.json`](../morphogenesis/experiments/R1_replicator/r1cap10_k1_seed7.json) | other | 1517 | `d485ec0a0446945b571d092beb77b86fa5c1f533e1e8b24968f190c054bc9b77` |
| [`morphogenesis/experiments/R1_replicator/r1cap10_k1_seed8.json`](../morphogenesis/experiments/R1_replicator/r1cap10_k1_seed8.json) | other | 1586 | `d229720066b49ba43cdb46741a3a286f2cc79c80b0278fb3db8c6a01ff4df3bd` |
| [`morphogenesis/experiments/R1_replicator/r1cap10_k1_seed9.json`](../morphogenesis/experiments/R1_replicator/r1cap10_k1_seed9.json) | other | 1502 | `b5a6206a89de85f62c714bd984bc95c9062285fe881dd092cc5f83517cf34062` |
| [`morphogenesis/experiments/R1_replicator/r1cap40_k1_seed1.json`](../morphogenesis/experiments/R1_replicator/r1cap40_k1_seed1.json) | other | 1561 | `52f31abe3cef67199f46dc9735171fcba863e05fbee3777d666631bd8d92c216` |
| [`morphogenesis/experiments/R1_replicator/r1cap40_k1_seed10.json`](../morphogenesis/experiments/R1_replicator/r1cap40_k1_seed10.json) | other | 1478 | `a64d661b89615f05d30914a80cd268745fd5fde8af4bc1f7cead53644cb39e1e` |
| [`morphogenesis/experiments/R1_replicator/r1cap40_k1_seed2.json`](../morphogenesis/experiments/R1_replicator/r1cap40_k1_seed2.json) | other | 1383 | `cf354493983c5568f1276e8e4f9f3255a0f20c522728028415e89ff7dc0a63d0` |
| [`morphogenesis/experiments/R1_replicator/r1cap40_k1_seed3.json`](../morphogenesis/experiments/R1_replicator/r1cap40_k1_seed3.json) | other | 1386 | `6e57d41c6c8e5b44f0fdcafce1267cc9afc46205577da91cadd30eab1e2bcf3d` |
| [`morphogenesis/experiments/R1_replicator/r1cap40_k1_seed4.json`](../morphogenesis/experiments/R1_replicator/r1cap40_k1_seed4.json) | other | 1547 | `17caa526d9fd8db790be6ebd635a0c0dd497a9e2a14f3eff3d0f5489970d5811` |
| [`morphogenesis/experiments/R1_replicator/r1cap40_k1_seed5.json`](../morphogenesis/experiments/R1_replicator/r1cap40_k1_seed5.json) | other | 1516 | `1ca6e0f76efa0316541b94cd8dbd10ad84e657c1adfc72211b745410e387086a` |
| [`morphogenesis/experiments/R1_replicator/r1cap40_k1_seed6.json`](../morphogenesis/experiments/R1_replicator/r1cap40_k1_seed6.json) | other | 1514 | `e25477397dc7d43a0890c3da4fd783f95da77522922cea52a9cc2b83bf241007` |
| [`morphogenesis/experiments/R1_replicator/r1cap40_k1_seed7.json`](../morphogenesis/experiments/R1_replicator/r1cap40_k1_seed7.json) | other | 1514 | `e85205408003bd4321325f78c793ecb275838075e5a7dac3e294c09006a583e4` |
| [`morphogenesis/experiments/R1_replicator/r1cap40_k1_seed8.json`](../morphogenesis/experiments/R1_replicator/r1cap40_k1_seed8.json) | other | 1573 | `75cdf21faf53dab2357a4cf3b99aa0f1c791a2e4a98315ed4fb90f072b70b8a1` |
| [`morphogenesis/experiments/R1_replicator/r1cap40_k1_seed9.json`](../morphogenesis/experiments/R1_replicator/r1cap40_k1_seed9.json) | other | 1500 | `169747aa59d8289dcc6267d636a140827cdee188dd7e18da344f9c3b7b65ab9e` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k1_seed1.json`](../morphogenesis/experiments/R1_replicator/r1cap_k1_seed1.json) | other | 1563 | `15a787930f59057cf2662de74dc5095fb61db0a8237eb06babcab70716c14f6d` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k1_seed10.json`](../morphogenesis/experiments/R1_replicator/r1cap_k1_seed10.json) | other | 1475 | `3f17d7fc9b0cf42ecc2c0ef5b0b087524d3d3a011ecc70ff40adc66c8b9a838c` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k1_seed2.json`](../morphogenesis/experiments/R1_replicator/r1cap_k1_seed2.json) | other | 1384 | `d4b56ec5a57603a44347156912272574196f66d5dba3c0f781572b25d5a54d62` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k1_seed3.json`](../morphogenesis/experiments/R1_replicator/r1cap_k1_seed3.json) | other | 1385 | `8158483c5b99ca7eed587a57a6d85ca046e3913267b3d86ecdbb8a0c392b01f2` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k1_seed4.json`](../morphogenesis/experiments/R1_replicator/r1cap_k1_seed4.json) | other | 1544 | `b824b347a47bdd5348077a3856df1210282e129b57971339d2d4e5d3f7cf6268` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k1_seed5.json`](../morphogenesis/experiments/R1_replicator/r1cap_k1_seed5.json) | other | 1521 | `7d3851c48ec93be1a36c0699877d2ff306a617b6cfb760a2d027d59dbc017c91` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k1_seed6.json`](../morphogenesis/experiments/R1_replicator/r1cap_k1_seed6.json) | other | 1520 | `bd6ed804efd9e0b4cc8412aa1dbd011ce01a6a0b2954184abfebc9111f051f71` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k1_seed7.json`](../morphogenesis/experiments/R1_replicator/r1cap_k1_seed7.json) | other | 1516 | `5e728b7ad16734cf1e4cde7ca5a8a00f99254afdcbd43cd006da54118dd49ced` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k1_seed8.json`](../morphogenesis/experiments/R1_replicator/r1cap_k1_seed8.json) | other | 1585 | `f376e10a2545ede3f3f22356b728c8587de7840706d1bd8b39b2cdaa33f0eb58` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k1_seed9.json`](../morphogenesis/experiments/R1_replicator/r1cap_k1_seed9.json) | other | 1502 | `a462db914a8b48622cd720b5a423f7867ff6193b502fcb039804fb01142b3db2` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k2_seed1.json`](../morphogenesis/experiments/R1_replicator/r1cap_k2_seed1.json) | other | 1609 | `1104c0f520bebc59dda593e1cdc49e94d17a80a73ab30edcf5815e3f8585e7ea` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k2_seed10.json`](../morphogenesis/experiments/R1_replicator/r1cap_k2_seed10.json) | other | 1550 | `caf225e42223a042b567e2dc6766cb1f73f33d4e83a4362c44366452a12261da` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k2_seed2.json`](../morphogenesis/experiments/R1_replicator/r1cap_k2_seed2.json) | other | 1517 | `f6fd3a8f33c37a74bda9640d1d651b284b994ad1fe648c29cf189938627c5ef7` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k2_seed3.json`](../morphogenesis/experiments/R1_replicator/r1cap_k2_seed3.json) | other | 1550 | `ed30de879d6c29d5c315d210c4e89a3270592cc82343f674109047335726fa88` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k2_seed4.json`](../morphogenesis/experiments/R1_replicator/r1cap_k2_seed4.json) | other | 1576 | `2adce93adcae4faa7f7d29cc2b9b0523fe9007c4e4e52126103f6f665d075b12` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k2_seed5.json`](../morphogenesis/experiments/R1_replicator/r1cap_k2_seed5.json) | other | 1580 | `6612f1393cc75ad38b8ee831cc7f6cc7e45487e65e72e7c4b6602e3f383cad1f` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k2_seed6.json`](../morphogenesis/experiments/R1_replicator/r1cap_k2_seed6.json) | other | 1602 | `249730485a4383c0b0efd173ff048bde25e2e8553b88391c6a9a9cee8392805c` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k2_seed7.json`](../morphogenesis/experiments/R1_replicator/r1cap_k2_seed7.json) | other | 1607 | `8a4de57d699ecbfddd6b6b5f5057a8f922d7f96f11d157ad16b8337e7e8a83d9` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k2_seed8.json`](../morphogenesis/experiments/R1_replicator/r1cap_k2_seed8.json) | other | 1636 | `9b79b87bae209e02889ec0deed45a463cb7222ec95801e5a6715055452996c2e` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k2_seed9.json`](../morphogenesis/experiments/R1_replicator/r1cap_k2_seed9.json) | other | 1577 | `8fa4ecbcaf3873bc852570b01ca60cb280081f2857c96ac7e61d49ad99d23839` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k8_seed1.json`](../morphogenesis/experiments/R1_replicator/r1cap_k8_seed1.json) | other | 1547 | `1daf82f2182019d925d5b0d8a6070a447d1c7cc127853fbcc4824597d3055ae6` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k8_seed10.json`](../morphogenesis/experiments/R1_replicator/r1cap_k8_seed10.json) | other | 1519 | `3bdf7521a8e907b5ee4ade19b97b6f43614a3c4bc167b276b94f47e0b2d2b128` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k8_seed2.json`](../morphogenesis/experiments/R1_replicator/r1cap_k8_seed2.json) | other | 1505 | `d56b395dbd33050d11f991203918abec011a3989989a7f031fe8d5c707b9e422` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k8_seed3.json`](../morphogenesis/experiments/R1_replicator/r1cap_k8_seed3.json) | other | 1536 | `afd41c475541368c1754b0861d36aa4853636f326f38f0bfb5a60b5dcc4fb505` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k8_seed4.json`](../morphogenesis/experiments/R1_replicator/r1cap_k8_seed4.json) | other | 1527 | `5f7d4698f288d282bcd10cda6eef18d8f3897f3c5e8a10fd72188e55de35b526` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k8_seed5.json`](../morphogenesis/experiments/R1_replicator/r1cap_k8_seed5.json) | other | 1515 | `4263f9235f6a47d22b073030ec56ecadead454bb0385c7e4c19c192941cfede1` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k8_seed6.json`](../morphogenesis/experiments/R1_replicator/r1cap_k8_seed6.json) | other | 1546 | `43ed9236e5c111e4817861190f30c6ac3bbfcc7acb276fb9a59b75a51e276b37` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k8_seed7.json`](../morphogenesis/experiments/R1_replicator/r1cap_k8_seed7.json) | other | 1546 | `f1f2c80df561bb8f587ecd851aaf3aab1570785d388f938b12ac87a249550307` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k8_seed8.json`](../morphogenesis/experiments/R1_replicator/r1cap_k8_seed8.json) | other | 1558 | `9e9c1957436805c57940087ad091615aaa03c2a3c8dc7bc4b9de67892df0ce14` |
| [`morphogenesis/experiments/R1_replicator/r1cap_k8_seed9.json`](../morphogenesis/experiments/R1_replicator/r1cap_k8_seed9.json) | other | 1532 | `daf0d1d11aa3413a6e0055fabf07ab8a390ad24e57b69b30e7543196e6336204` |
| [`morphogenesis/experiments/R1_replicator/r1cap_matrix.json`](../morphogenesis/experiments/R1_replicator/r1cap_matrix.json) | other | 14877 | `9a842941527f2b3d55d5c35451130be1a1a17a22eaacc4c735e9adb0ae109cde` |
| [`reports/figures/2026-10-26-arxiv-fig1.png`](../reports/figures/2026-10-26-arxiv-fig1.png) | figure | 91841 | `67b96ea56c1cf30ce6150a40df8a4ad18217f98037af37c5b32689417b97a13e` |
| [`reports/figures/2026-10-26-arxiv-fig2.png`](../reports/figures/2026-10-26-arxiv-fig2.png) | figure | 78352 | `0c06409fc184b12b8241137d2dca2b6e78b62d98df7e2a03cd6e049610726415` |
| [`reports/figures/2026-10-26-arxiv-fig3.png`](../reports/figures/2026-10-26-arxiv-fig3.png) | figure | 101970 | `ce4715f194a44eb22c798b9da86c8eb71918e43a2f1ea61ec89443f19bddb107` |
| [`reports/figures/2026-10-26-arxiv-fig4.png`](../reports/figures/2026-10-26-arxiv-fig4.png) | figure | 85657 | `78a42541a1b54c14ab27a51e706da10f649c6ff1fb438e0d978e81cf2bbbf19a` |
| [`reports/figures/day-2026-10-25-objects.png`](../reports/figures/day-2026-10-25-objects.png) | figure | 274830 | `1e50294dae89b4312dae0c1829982571a6a6f4ed3c6dbb219fac56aefc1a9725` |
| [`reports/figures/day-2026-10-25-simple.png`](../reports/figures/day-2026-10-25-simple.png) | figure | 237542 | `38e50662a0dd58d6d943bd38cc3166b7fa798ad8dadb5287b55796431f830021` |
| [`reports/figures/day-2026-10-25.png`](../reports/figures/day-2026-10-25.png) | figure | 334254 | `9bd43d551def60017ae79a746f5542163499e693f97d6e3bd021bad69d0dd8a4` |
| [`reports/figures/e02b_asymmetry_pairs.png`](../reports/figures/e02b_asymmetry_pairs.png) | figure | 68781 | `86caa9ac8e0d4fbf86b3f7b0f8a25f1eae17a484aa3ab49c9307c7b9819337f6` |
| [`reports/figures/e02b_carrier_map.png`](../reports/figures/e02b_carrier_map.png) | figure | 140540 | `57303664767fffe01c3633cb569cf8c84b3cdaf3d15f2b1950818db45fc6a02f` |
| [`reports/figures/e02b_geometry_of_form.png`](../reports/figures/e02b_geometry_of_form.png) | figure | 150644 | `2d2c6898df2b4aee799309cc1d5a6fe877128d36613370410b5353de0605f241` |
| [`reports/figures/e02b_morphospace_pca.png`](../reports/figures/e02b_morphospace_pca.png) | figure | 95345 | `90aa1bad3f8a040a4ec11585b9b20966698f4af5ca3ea867b9d73849fe282443` |
| [`reports/figures/e02b_patch_identity_struct_1_s16.png`](../reports/figures/e02b_patch_identity_struct_1_s16.png) | figure | 21182 | `f5d7817a5e93f61064db38e4ab2ee20ae0d6cd97d2f9e919d2bdeb62afee3632` |
| [`reports/figures/e02b_patch_identity_struct_1_s32.png`](../reports/figures/e02b_patch_identity_struct_1_s32.png) | figure | 21318 | `d183710cfa9c5323069630d1af1cb01fb6726d6152bc9ed89c72622d9360108b` |
| [`reports/figures/e02b_patch_identity_struct_1_s8.png`](../reports/figures/e02b_patch_identity_struct_1_s8.png) | figure | 20911 | `ff19c4896abc63da0c4530890874684e83a7d12a0e9565f41f4fb18c72cf7c13` |
| [`reports/figures/e02b_patch_identity_struct_2_s16.png`](../reports/figures/e02b_patch_identity_struct_2_s16.png) | figure | 18709 | `6a060e2d317898d6388b1afa4be1af4d2090dd8815e668e4b421524953490084` |
| [`reports/figures/e02b_patch_identity_struct_2_s32.png`](../reports/figures/e02b_patch_identity_struct_2_s32.png) | figure | 17687 | `f98d5f356f851e6b2bc3dbb5eb5903215817683781f6fcc485e0e23bee1c1cd7` |
| [`reports/figures/e02b_patch_identity_struct_2_s8.png`](../reports/figures/e02b_patch_identity_struct_2_s8.png) | figure | 18156 | `ddd410ea908cd0e77a555485e8edf5626d96889f8e598e91978c58f6eda2b3d2` |
| [`reports/figures/e02b_struct_1_WP4_R-9_s2000_seed101_s25.png`](../reports/figures/e02b_struct_1_WP4_R-9_s2000_seed101_s25.png) | figure | 31684 | `7ce4d10d81571d13f2e4c9576fdda625bdb04f66315579fc0388338af4b47184` |
| [`reports/figures/e02b_struct_1_WP4_R-9_s2000_seed101_s41.png`](../reports/figures/e02b_struct_1_WP4_R-9_s2000_seed101_s41.png) | figure | 31385 | `a8ae888778a228df908cd1b57a3329bf3d25934e258e40c6781feefae0bb9022` |
| [`reports/figures/e02b_struct_1_WP4_R-9_s2000_seed101_s5.png`](../reports/figures/e02b_struct_1_WP4_R-9_s2000_seed101_s5.png) | figure | 31667 | `d956ae46a3eb2c92eba935b458fb6d19cb26937b5658a4b7b41a9b81d472a614` |
| [`reports/figures/e02b_struct_2_WP4_R-9_s2000_seed42_s3.png`](../reports/figures/e02b_struct_2_WP4_R-9_s2000_seed42_s3.png) | figure | 16507 | `d2c20eda232426a8644273e39b6737f979c91c0a98d9ad7d1dafe4efbbe1f264` |
| [`reports/figures/e02b_struct_2_WP4_R-9_s2000_seed42_s35.png`](../reports/figures/e02b_struct_2_WP4_R-9_s2000_seed42_s35.png) | figure | 16760 | `0d067f95b54f5ed5f84b9f9ab35befdf961b09c9d7380f0bdf01bc234362451f` |
| [`reports/figures/e02b_struct_2_WP4_R-9_s2000_seed42_s53.png`](../reports/figures/e02b_struct_2_WP4_R-9_s2000_seed42_s53.png) | figure | 16944 | `7ff71dc32e970a944eabd5221141f98275f0f8ed8ce4e5e6d03745d0b03e0e13` |
| [`reports/figures/e02b_transition_matrix.png`](../reports/figures/e02b_transition_matrix.png) | figure | 152522 | `81f1b4fe50fd819f45411c31fb737a0c232d9c4f993f5233184c8b276779f5b9` |
| [`reports/figures/e02c_seed_grid.png`](../reports/figures/e02c_seed_grid.png) | figure | 69503 | `a14f0a6eb28fa0675629e539dc863049d97c3a7ef1914c34ebd7348b5c71776f` |
<!-- artifacts:end -->











































































































































































































































































































































































































































































































































































































































































































































































