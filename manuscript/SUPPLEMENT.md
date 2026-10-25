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
| [`lab/checkpoints.json`](../lab/checkpoints.json) | index | 9472 | `a502dfaed723376de1bcca1960bd7b53d97c5a2d5da5998cdb54edb6ded2cdbc` |
| [`lab/registry.json`](../lab/registry.json) | index | 190268 | `7edbf95c0ab10d479481fc96f24fd6b78b09e0548d561c4b31b80b2c00d27e3d` |
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
| [`morphogenesis/experiments/E09_pond/b2_matrix.json`](../morphogenesis/experiments/E09_pond/b2_matrix.json) | other | 4832 | `92aab1622380af299e8b5c8beedbcbc8ae91999eb5fe670fd416a9b3a421bb77` |
| [`morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed1.json`](../morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed1.json) | other | 130063 | `fdb73048896daf327bfe5cc79b99715dc90c807907ce6ecd4a9ff32a1d38769c` |
| [`morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed2.json`](../morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed2.json) | other | 129542 | `b33a7aef273f8a8f72dfc8c51352712b1704bf1e9fc6b6a5e685df8720d890e4` |
| [`morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed3.json`](../morphogenesis/experiments/E09_pond/b2d_patches_adapt_seed3.json) | other | 128661 | `3853a8f8b485d5e0806b9c9c2d62f8589782fb7c84aa49f626560173912747d8` |
| [`morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed1.json`](../morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed1.json) | other | 129809 | `4e6bd23ee40f104b99e9922fef854a1ae620bc0a99e31fa7d0ad8ec2fa6d3420` |
| [`morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed2.json`](../morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed2.json) | other | 129940 | `b9f221a47094bf927d52a07de791d772cd498afa7023e4db64d2f65110b4a297` |
| [`morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed3.json`](../morphogenesis/experiments/E09_pond/b2d_uniform_adapt_seed3.json) | other | 129646 | `d427c1ab26e33b14dda2d89812820aa58ad18ae59fd7bcc234755ba73e815b14` |
| [`morphogenesis/experiments/E09_pond/catastrophe_diversity.json`](../morphogenesis/experiments/E09_pond/catastrophe_diversity.json) | other | 23191 | `0c342669c9a8ea6059c8a00ca9cf7a75fd634a8eeae3c9e801f9d24873c6570a` |
| [`morphogenesis/experiments/E09_pond/catastrophe_matrix.json`](../morphogenesis/experiments/E09_pond/catastrophe_matrix.json) | other | 21052 | `ce28440d2ce8a3b35bf8104fcd96c72860c6ef5ca5c3f4618636de33982ed1de` |
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
| [`morphogenesis/experiments/E09_pond/colony_type_matrix.json`](../morphogenesis/experiments/E09_pond/colony_type_matrix.json) | other | 13012 | `c8497ce4b6e5520f1ac26669db9c52a655e9d8bf9ab0eae5adb1362eda2ef5fe` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_base.json`](../morphogenesis/experiments/E09_pond/diag_ignition_base.json) | other | 128332 | `b18a23673e15e8bb455726c9fc8a886995ffc567db0afc3c6e946b786dddfc7f` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_gate.json`](../morphogenesis/experiments/E09_pond/diag_ignition_gate.json) | other | 112669 | `d077adf2a67087d6fd806f28173d637579a8718a47ad206ae9bc20825650fc00` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_nofill.json`](../morphogenesis/experiments/E09_pond/diag_ignition_nofill.json) | other | 126844 | `fd7a22b2d9fea04791a7737f297decc7f0d63e873085693768e3fa5c865f3090` |
| [`morphogenesis/experiments/E09_pond/diag_ignition_noincome.json`](../morphogenesis/experiments/E09_pond/diag_ignition_noincome.json) | other | 117172 | `edf7d2eb084f907d6bde547d73f1c13080c4f2482ee2276d71cf70a255c4b295` |
| [`morphogenesis/experiments/E09_pond/drift_matrix.json`](../morphogenesis/experiments/E09_pond/drift_matrix.json) | other | 4939 | `8757b3d3aabc61e1511e63f97a7afda79a2b28089b167c0542a01377477a739e` |
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
| [`morphogenesis/experiments/E09_pond/frequency_matrix.json`](../morphogenesis/experiments/E09_pond/frequency_matrix.json) | other | 16139 | `edf3f4fec02d2208867102d1d6d6e5b46b4749f0558061c1eff90a23367f4e3f` |
| [`morphogenesis/experiments/E09_pond/frequency_matrix_v2.json`](../morphogenesis/experiments/E09_pond/frequency_matrix_v2.json) | other | 21150 | `1dd28d144e5c7af6e065942d4acd595762829370cb92a0e1d41b78b61a1d2c28` |
| [`morphogenesis/experiments/E09_pond/frequency_start_control.json`](../morphogenesis/experiments/E09_pond/frequency_start_control.json) | other | 5116 | `695b70a367873122d7818f72ce11a4b140fe5820927c5fa487cbe15783db2509` |
| [`morphogenesis/experiments/E09_pond/generation_matrix.json`](../morphogenesis/experiments/E09_pond/generation_matrix.json) | other | 5854 | `53eea082ae7597d848cee4be051bb31142b7fd49f4f8aba2a9bb1e1ab91dcab8` |
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
| [`morphogenesis/experiments/E09_pond/invader_dose_matrix.json`](../morphogenesis/experiments/E09_pond/invader_dose_matrix.json) | other | 36490 | `17d14e144c0c0b98b16ab698255a8a8cc8b871a8307fd9849749b1f245470e5f` |
| [`morphogenesis/experiments/E09_pond/invasion_matrix.json`](../morphogenesis/experiments/E09_pond/invasion_matrix.json) | other | 5076 | `816a35ba39edaf91525328e0e987effcbc319e54d3bd3ec6a31b148f4215c5f7` |
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
| [`morphogenesis/experiments/E09_pond/l2_matrix.json`](../morphogenesis/experiments/E09_pond/l2_matrix.json) | other | 7822 | `999dcb35b5ebeaaaa53e6284a62002ced2255ed7ae32affab94af61e67ca85e9` |
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
| [`morphogenesis/experiments/E09_pond/mobility_matrix.json`](../morphogenesis/experiments/E09_pond/mobility_matrix.json) | other | 11050 | `2f9fc5f10c30690c217a55c28301e76049fdcc2b30ab3cbaf57073b27d21fe0f` |
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
| [`morphogenesis/experiments/E09_pond/mutation_matrix.json`](../morphogenesis/experiments/E09_pond/mutation_matrix.json) | other | 14527 | `1c044b1b4dfc1ab1e57797b52569e684202b2c3ee5fe9c6adbe39c9650447086` |
| [`morphogenesis/experiments/E09_pond/organism_mobility_matrix.json`](../morphogenesis/experiments/E09_pond/organism_mobility_matrix.json) | other | 8615 | `0f567a40bcb390b6e4d061656c648199311ff0292b79a8a5696db2f507416987` |
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
| [`morphogenesis/experiments/E09_pond/sense_noise_matrix.json`](../morphogenesis/experiments/E09_pond/sense_noise_matrix.json) | other | 13884 | `7a234b6805c321e61c54ba3fea23d15433923b0ae0297c0d8f9af726f96b5e0f` |
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
| [`morphogenesis/experiments/E09_pond/w2bud2_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud2_matrix.json) | other | 30576 | `db2e47f4ebb5028f23e74a860a09199d11a70d3c87594a9198a2bf6a94400d19` |
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
| [`morphogenesis/experiments/E09_pond/w2bud3_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud3_matrix.json) | other | 30624 | `fe13da5af908b361963c3389ca476acfb58b5e5cf3fa738a20e32d1ef8504392` |
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
| [`morphogenesis/experiments/E09_pond/w2bud4s_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud4s_matrix.json) | other | 18200 | `91734d6756b6dcf5aee2f855de935a14da7481253ddd4958d742918cc285bcf9` |
| [`morphogenesis/experiments/E09_pond/w2bud_matrix.json`](../morphogenesis/experiments/E09_pond/w2bud_matrix.json) | other | 30581 | `3815528981e4fca9936e2ed86c72be370930c25699d7cdcbbd73fdb71fcdf616` |
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












































































































