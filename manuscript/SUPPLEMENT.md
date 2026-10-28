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
| [`lab/checkpoints.json`](../lab/checkpoints.json) | index | 11024 | `fc6dbce037ae3f84d0b49dba9611767d26412d4c32e12a948b736251f32554f5` |
| [`lab/registry.json`](../lab/registry.json) | index | 198656 | `bef74b7516d7e64e71c1be8676d43274c882c8d22b0041e71807fb474afec71f` |
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
| [`morphogenesis/experiments/E09_pond/b2_matrix.json`](../morphogenesis/experiments/E09_pond/b2_matrix.json) | other | 4832 | `92aab1622380af299e8b5c8beedbcbc8ae91999eb5fe670fd416a9b3a421bb77` |
| [`morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed1.json`](../morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed1.json) | other | 130063 | `fdb73048896daf327bfe5cc79b99715dc90c807907ce6ecd4a9ff32a1d38769c` |
| [`morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed2.json`](../morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed2.json) | other | 129542 | `b33a7aef273f8a8f72dfc8c51352712b1704bf1e9fc6b6a5e685df8720d890e4` |
| [`morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed3.json`](../morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed3.json) | other | 128661 | `3853a8f8b485d5e0806b9c9c2d62f8589782fb7c84aa49f626560173912747d8` |
| [`morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed1.json`](../morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed1.json) | other | 129809 | `4e6bd23ee40f104b99e9922fef854a1ae620bc0a99e31fa7d0ad8ec2fa6d3420` |
| [`morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed2.json`](../morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed2.json) | other | 129940 | `b9f221a47094bf927d52a07de791d772cd498afa7023e4db64d2f65110b4a297` |
| [`morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed3.json`](../morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed3.json) | other | 129646 | `d427c1ab26e33b14dda2d89812820aa58ad18ae59fd7bcc234755ba73e815b14` |
| [`morphogenesis/experiments/E09_pond/catastrophe_diversity.json`](../morphogenesis/experiments/E09_pond/catastrophe_diversity.json) | other | 23620 | `38aa7dcc80f46d1540bac554ba6e546459dcc3c74e9d1dd8c1c500c0c6bed50b` |
| [`morphogenesis/experiments/E09_pond/catastrophe_matrix.json`](../morphogenesis/experiments/E09_pond/catastrophe_matrix.json) | other | 23715 | `a286d4729ceceb0d1301cc981d6d507acdbc1c991cb361343b5802606bcef61e` |
| [`morphogenesis/experiments/E09_pond/coexistence_matrix.json`](../morphogenesis/experiments/E09_pond/coexistence_matrix.json) | other | 34410 | `e1f53958b1e7f080ea6905597f8631613a10b0acfc81fbda5a95eb2154275469` |
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
| [`morphogenesis/experiments/E09_pond/colony_type_matrix.json`](../morphogenesis/experiments/E09_pond/colony_type_matrix.json) | other | 13506 | `ba87f25cd5b8fe87a7a3b670fc4d19a39b70bb7f6f193f17fd14ca122fc97ab6` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_base.json`](../morphogenesis/experiments/E09_pond/diag_ignition_base.json) | other | 128332 | `b18a23673e15e8bb455726c9fc8a886995ffc567db0afc3c6e946b786dddfc7f` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_gate.json`](../morphogenesis/experiments/E09_pond/diag_ignition_gate.json) | other | 112669 | `d077adf2a67087d6fd806f28173d637579a8718a47ad206ae9bc20825650fc00` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_nofill.json`](../morphogenesis/experiments/E09_pond/diag_ignition_nofill.json) | other | 126844 | `fd7a22b2d9fea04791a7737f297decc7f0d63e873085693768e3fa5c865f3090` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_noincome.json`](../morphogenesis/experiments/E09_pond/diag_ignition_noincome.json) | other | 117172 | `edf7d2eb084f907d6bde547d73f1c13080c4f2482ee2276d71cf70a255c4b295` |
| [`morphogenesis/experiments/E09_pond/drift_matrix.json`](../morphogenesis/experiments/E09_pond/drift_matrix.json) | other | 6000 | `14dc75196198a1d27e290eec60d39e6f1d6688556e4a87948d3be0dde745c19d` |
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
| [`morphogenesis/experiments/E09_pond/founding_matrix.json`](../morphogenesis/experiments/E09_pond/founding_matrix.json) | other | 28143 | `ba1ecf2e493792de00915196f45ce3729bd9bcc2bb41bdf419cb7544fe873368` |
| [`morphogenesis/experiments/E09_pond/frequency_matrix.json`](../morphogenesis/experiments/E09_pond/frequency_matrix.json) | other | 18640 | `8297a455da054694e943290cbdade0f799cd045d09993daea73f2b9b5b5e6e36` |
| [`morphogenesis/experiments/E09_pond/frequency_matrix_v2.json`](../morphogenesis/experiments/E09_pond/frequency_matrix_v2.json) | other | 24234 | `689782d2fcb7ebb828eade5c2fdb9d985459296b0c343ae22efc11a5cff3c092` |
| [`morphogenesis/experiments/E09_pond/frequency_start_control.json`](../morphogenesis/experiments/E09_pond/frequency_start_control.json) | other | 6007 | `8a09a2a49002ca3378f27d7259f93814097ab52bdfda7644e05cbf77a1841159` |
| [`morphogenesis/experiments/E09_pond/generation_matrix.json`](../morphogenesis/experiments/E09_pond/generation_matrix.json) | other | 6348 | `2716717815a1ef8678bea45eca72f7109b2be4ad02a2b08a0a507df4ab75df49` |
| [`morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed1.json`](../morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed1.json) | other | 166248 | `4332cbf28f616fd9a787324265ba12c1ee6a692b5f8766b1f2cba13aaf21522b` |
| [`morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed2.json`](../morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed2.json) | other | 166809 | `62a42401e58d28f81451663bd7cb41c38e1daab2a542afb6ebbd355f49769244` |
| [`morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed3.json`](../morphogenesis/experiments/E09_pond/genprobe_gradflip_fixed_seed3.json) | other | 166373 | `b2369ace72c1c8802b4a59836010075c14547f5a4694b4599bde62904a50a09c` |
| [`morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed1.json`](../morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed1.json) | other | 148518 | `aa8b5802025697e5830e5a565a9403d7913bda1f22996884a662e7354cbc45aa` |
| [`morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed2.json`](../morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed2.json) | other | 166554 | `b1bba692ea109bd58893cc079fe93baa83adc4d05091e86c12482202097b31fc` |
| [`morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed3.json`](../morphogenesis/experiments/E09_pond/genprobe_patches_fixed_seed3.json) | other | 166601 | `1cdd19757875dc2f96013741597c4be46322a282db78ce00536013f41ce11d9d` |
| [`morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed1.json`](../morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed1.json) | other | 166101 | `374c196bd2e6418d4cb2842a3f2baf419b1d8e329c60ce05e5d0057615380dc4` |
| [`morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed2.json`](../morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed2.json) | other | 166639 | `16bfd2960b7f63ea0a45d9b3d14b41abc3afa9572ed00230af0bc26816d16796` |
| [`morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed3.json`](../morphogenesis/experiments/E09_pond/genprobe_uniform_fixed_seed3.json) | other | 166227 | `3876ffbfa5fe5a28a177966e5a5cdd6827551f973d043f120db17ea71f466e29` |
| [`morphogenesis/experiments/E09_pond/inherit2_gradflip_fixed.json`](../morphogenesis/experiments/E09_pond/inherit2_gradflip_fixed.json) | other | 1564 | `7afabe8f08591035e95c5d57244e52ee7f4a9b4d4ec5dbd931800df4afb2f798` |
| [`morphogenesis/experiments/E09_pond/inherit2_patches_fixed.json`](../morphogenesis/experiments/E09_pond/inherit2_patches_fixed.json) | other | 1562 | `0da84ca1f69206c8da5a6721c8604202226904ddf92156b6c6b38d96d118638a` |
| [`morphogenesis/experiments/E09_pond/inherit2_uniform_fixed.json`](../morphogenesis/experiments/E09_pond/inherit2_uniform_fixed.json) | other | 1566 | `24d8e5a2da7b7cf772655a83594c1c34553f05d3a478b92f779c20b2bc388295` |
| [`morphogenesis/experiments/E09_pond/invader_death_matrix.json`](../morphogenesis/experiments/E09_pond/invader_death_matrix.json) | other | 12503 | `bf80bf1551d5ea5bae57abafa44fc376af4bc3da7aac082698fb6597af098f61` |
| [`morphogenesis/experiments/E09_pond/invader_dose_matrix.json`](../morphogenesis/experiments/E09_pond/invader_dose_matrix.json) | other | 36984 | `587c2293728b8ca7ba2b69305f8a76dd800621e90373e682fee2cd19da013461` |
| [`morphogenesis/experiments/E09_pond/invasion_matrix.json`](../morphogenesis/experiments/E09_pond/invasion_matrix.json) | other | 6059 | `14dd7bb7a426f9f52ff6316714820fc9ecc96cfdfcbd377008006ed2169ffa5f` |
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
| [`morphogenesis/experiments/E09_pond/kill_keep2_matrix.json`](../morphogenesis/experiments/E09_pond/kill_keep2_matrix.json) | other | 6826 | `60a8e57eb90b5e8366b7a8f4feca0b6c7e616b43516a67f36f34c33977a2f352` |
| [`morphogenesis/experiments/E09_pond/kill_keep3_matrix.json`](../morphogenesis/experiments/E09_pond/kill_keep3_matrix.json) | other | 6828 | `3ecea48b2d97c42892e4f4b06d2e17d5dadd4f99d95d20c48f74a33c48b24f47` |
| [`morphogenesis/experiments/E09_pond/kill_keep_matrix.json`](../morphogenesis/experiments/E09_pond/kill_keep_matrix.json) | other | 5550 | `17ee3876982eea05617d04ec4f9acf37b7a8d4e8889fa6056e212f818ee63b0f` |
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
| [`morphogenesis/experiments/E09_pond/l2_matrix.json`](../morphogenesis/experiments/E09_pond/l2_matrix.json) | other | 9165 | `f1859c3cee0d30fc292e6e9349cbbdef3e653f587bd3f6f0a2860791c9426e62` |
| [`morphogenesis/experiments/E09_pond/merge_keep_matrix.json`](../morphogenesis/experiments/E09_pond/merge_keep_matrix.json) | other | 17154 | `fdcdad726dc0fd9b44abc998e9fbe802c813682a7e3ebca336db78d4c03f25d8` |
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
| [`morphogenesis/experiments/E09_pond/mobility_matrix.json`](../morphogenesis/experiments/E09_pond/mobility_matrix.json) | other | 12885 | `2ff68c26431fb8c9fe5965d4c4036e756d1823a36b4c89bc5637c26a490249dc` |
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
| [`morphogenesis/experiments/E09_pond/mutation_matrix.json`](../morphogenesis/experiments/E09_pond/mutation_matrix.json) | other | 15021 | `bf919c0f56cdf62c37461a0762ae747b0714a7d0ff3b19803cd5699309df67c5` |
| [`morphogenesis/experiments/E09_pond/organism_mobility_matrix.json`](../morphogenesis/experiments/E09_pond/organism_mobility_matrix.json) | other | 10117 | `f27fb4591b56572b7e1f8771c86555e4c9b7576ab126f8d293d23856d6a6222e` |
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
| [`morphogenesis/experiments/E09_pond/phase_matrix.json`](../morphogenesis/experiments/E09_pond/phase_matrix.json) | other | 16796 | `fdca54a9b773bb736608001ee31cd3560d06849ef110536079c780321c15876e` |
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
| [`morphogenesis/experiments/E09_pond/placement_matrix.json`](../morphogenesis/experiments/E09_pond/placement_matrix.json) | other | 11972 | `103f2b85d53b21f107016a0ea0774664703bf78fd205c93e6982475fdd92bf8d` |
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
| [`morphogenesis/experiments/E09_pond/placement_patches_matrix.json`](../morphogenesis/experiments/E09_pond/placement_patches_matrix.json) | other | 12263 | `392a99ea4630c2da62f0a086dab4ad5812a5359c606585ded223944cdaf026ab` |
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
| [`morphogenesis/experiments/E09_pond/sel_eps00_seed1.json`](../morphogenesis/experiments/E09_pond/sel_eps00_seed1.json) | other | 481086 | `0644afa43f842e7c1a3dc1cc5bfcd94a06f754b08b35511c240aa5101d7c38b6` |
| [`morphogenesis/experiments/E09_pond/sel_eps00_seed2.json`](../morphogenesis/experiments/E09_pond/sel_eps00_seed2.json) | other | 468098 | `4d1da28190f00667b6251d50e6ead3525f16f5a80c47877afc97b2378176831c` |
| [`morphogenesis/experiments/E09_pond/sel_eps00_seed3.json`](../morphogenesis/experiments/E09_pond/sel_eps00_seed3.json) | other | 477211 | `eb4a8736b0f62fa85bda0a6ddb5fdaf78c66de21c4ee0efa9b65d14c75d6220e` |
| [`morphogenesis/experiments/E09_pond/sel_eps200_seed1.json`](../morphogenesis/experiments/E09_pond/sel_eps200_seed1.json) | other | 478401 | `a72616e445067f3816732e565d134335d35c202955291e70af941214bdcd199a` |
| [`morphogenesis/experiments/E09_pond/selection_matrix.json`](../morphogenesis/experiments/E09_pond/selection_matrix.json) | other | 5756 | `3c1cda812eb30bfcca7f7ccdcbd4933484d18cab7c96a8fb8cf0cdd3e5a3e62d` |
| [`morphogenesis/experiments/E09_pond/sense_noise_matrix.json`](../morphogenesis/experiments/E09_pond/sense_noise_matrix.json) | other | 16247 | `a424f59cbae916170bf900db1cb5fc8a0b91867fc981f23fd16c853fbd16b0d6` |
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
| [`morphogenesis/experiments/E09_pond/v8_matrix.json`](../morphogenesis/experiments/E09_pond/v8_matrix.json) | other | 40012 | `764390fd4360bc91972f3a36be90f740e72d32934b1f2dd67fbbba151bf9478d` |
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
| [`morphogenesis/experiments/E09_pond/w1niche5_matrix.json`](../morphogenesis/experiments/E09_pond/w1niche5_matrix.json) | other | 26277 | `54764a45a54b2eda5b43e0ffb1f1d5d6772f0c3e2b1cd6cb5591e41e8decf2ea` |
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
| [`morphogenesis/experiments/E09_pond/w1niche_free_matrix.json`](../morphogenesis/experiments/E09_pond/w1niche_free_matrix.json) | other | 12913 | `4f1cf09f5909554cbd69128459a6e72bba0a1a540d2524e68252da78586cd607` |
| [`morphogenesis/experiments/E09_pond/w1niche_matrix.json`](../morphogenesis/experiments/E09_pond/w1niche_matrix.json) | other | 35007 | `ea7511412d8dec986822ca4bbe1c4a3f915d527e4ddc1cf41afc295c9a58907f` |
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
| [`morphogenesis/experiments/E09_pond/w2bud2_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud2_matrix.json) | other | 34856 | `13e62117c8966e2ed94c83ea06fca369db6308fc093f81af595927281ad14086` |
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
| [`morphogenesis/experiments/E09_pond/w2bud3_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud3_matrix.json) | other | 34904 | `9cf2e73b6e019241a68e8b080046963e9d4a06543b4214ce273337b7a05f12f8` |
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
| [`morphogenesis/experiments/E09_pond/w2bud4s_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud4s_matrix.json) | other | 19529 | `7cefc2476b4604427162fbc4fac8ecbd723bd4e0f92c859a741a9d50ff2ba726` |
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
| [`morphogenesis/experiments/E09_pond/w2bud_additivity_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_additivity_matrix.json) | other | 66239 | `568c9f5444e47e5d959f6a847fb663d1a475916088f91f16c7b4aeda1a5553a0` |
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
| [`morphogenesis/experiments/E09_pond/w2bud_async_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_async_matrix.json) | other | 96837 | `3f205805d21e6e30add8229533f3b19d6393a33c8ffc5b9be714ba72185e2784` |
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
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm_matrix.json) | other | 50130 | `1bec6a8956b5468f44da7951d1f13abe7fbb4898b770b23ca2a32c48f53471c5` |
| [`morphogenesis/experiments/E09_pond/w2bud_killwinner_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_killwinner_matrix.json) | other | 50793 | `769026d1dbd43ef5a59baaae0982f2b0c998ed033ea96de0850016cae5798e6a` |
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
| [`morphogenesis/experiments/E09_pond/w2bud_lines_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_lines_matrix.json) | other | 7626 | `d65a5801ccc1197a5e9517db2df992e6f25813c3c80247ef360a580d6b7179e4` |
| [`morphogenesis/experiments/E09_pond/w2bud_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_matrix.json) | other | 34862 | `e7c676f07e0f9dd4840701c09590cf0dca8b624d236767b2c75892f6ae99dd11` |
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
| [`morphogenesis/experiments/E09_pond/w2bud_onebud_fisher_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud_fisher_matrix.json) | other | 7870 | `6363eb723f9f9802c2951510e509380fd8c47954009578d64b78bc0fc21009e5` |
| [`morphogenesis/experiments/E09_pond/w2bud_onebud_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_onebud_matrix.json) | other | 41360 | `37a1c02962f5fdbb202f8ba404ae34c842d7b92a4e3812a70d5e1eddb70689d2` |
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
| [`morphogenesis/experiments/E09_pond/w2bud_pair_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_pair_matrix.json) | other | 19646 | `9f69e164dfe68a56ab1cc343595374bbf9d7424b5f6c5ebcca5254cdfe838c0c` |
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
| [`morphogenesis/experiments/E09_pond/w2bud_pairany_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_pairany_matrix.json) | other | 19673 | `37676597e7ce7eaff15fac3cb747631606d3e1cd1008cb95de7a0aa5eb8f5625` |
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
| [`morphogenesis/experiments/E09_pond/w2bud_quota_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_quota_matrix.json) | other | 49184 | `eda92dd380543df1b062b2c56038aefe2dabd0aa0244cf1730fcb5433a9e42fe` |
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
| [`morphogenesis/experiments/E09_pond/w2bud_rep_patches_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_patches_matrix.json) | other | 18841 | `dba450b5a97861d5651eee3d66861de1cf2b52c0cd050bf83eeb4f3e692cf050` |
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
| [`morphogenesis/experiments/E09_pond/w2bud_rep_uniform_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_rep_uniform_matrix.json) | other | 33657 | `a0f60c8331ffb579493763ee2d6c2287d6db6f9f4207ff6430dcf8348a4ed387` |
| [`morphogenesis/experiments/E09_pond/w2bud_stream/w2bud_stream_cellc_seed171.json`](../morphogenesis/experiments/E09_pond/w2bud_stream/w2bud_stream_cellc_seed171.json) | other | 619963 | `6b6dd9c7a577bf3a9027562092f1763b530bdb82abf147b243de366ae87416e3` |
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
| [`morphogenesis/experiments/E09_pond/w2bud_trait_update_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_trait_update_matrix.json) | other | 33716 | `c7208f29d70c4af6d49ee431e338f5945e0d84026d9bd99c8c52e4b7555aca76` |
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
| [`morphogenesis/experiments/E09_pond/w2budd2_matrix.json`](../morphogenesis/experiments/E09_pond/w2budd2_matrix.json) | other | 19318 | `80fc00a894a67bba7216e0abb514aeec99b401249ea772fae04048b481f1661f` |
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
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_matrix.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_matrix.json) | other | 19314 | `cd145d80e3aa853de7a352c85abd99d52c3a5301e238b19db1efbf2d2cb459e9` |
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
| [`morphogenesis/experiments/E09_pond/w2budd2_rep_n1_matrix.json`](../morphogenesis/experiments/E09_pond/w2budd2_rep_n1_matrix.json) | other | 19384 | `2487a916b545953513d656ec7251cc91f17f302ef25c70753e21ad72cf6a4333` |
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
| [`morphogenesis/experiments/R1_replicator/r1_matrix.json`](../morphogenesis/experiments/R1_replicator/r1_matrix.json) | other | 14099 | `a98f64e86eddcd5969e90bdd2c586c1aec26080d44b8ffe1df2daca4ba49dc05` |
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
| [`morphogenesis/experiments/R1_replicator/r1cap_matrix.json`](../morphogenesis/experiments/R1_replicator/r1cap_matrix.json) | other | 14165 | `4b3bd7a292717392b0dbe31da8c56828b6224fd7a26567bd848328bf9b065a12` |
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

































































































































































































































































































