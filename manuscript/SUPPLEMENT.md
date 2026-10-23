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
| [`lab/registry.json`](../lab/registry.json) | index | 165791 | `17efca5698b96a5c9b459766827683afbd453ea21823a983ce2ebe3eada6c5d1` |
| [`morphogenesis/experiments/E01_criticality/frame_000050.png`](../morphogenesis/experiments/E01_criticality/frame_000050.png) | figure | 19729 | `bda8c5610091556a26bc58b18dd0cecdfa8da8d758c1f7fbdd4d2be2ce423a42` |
| [`morphogenesis/experiments/E01_criticality/lyapunov_scan.json`](../morphogenesis/experiments/E01_criticality/lyapunov_scan.json) | other | 1680 | `0fbb88573d36001ba0bc4634d58223272db6b0456e72df6e261c62aab4ef1016` |
| [`morphogenesis/experiments/E01_criticality/results.json`](../morphogenesis/experiments/E01_criticality/results.json) | other | 2996 | `a9ca8a26091315512b4a07b15731db9fc9eacfc821748b013d8d39a50a28c322` |
| [`morphogenesis/experiments/E02_pattern/collapse_probe.json`](../morphogenesis/experiments/E02_pattern/collapse_probe.json) | other | 23194 | `d5f2472ea4938ca796e52d0158064f00c7c6a7b2de6b38c2c9474b0f484dd68b` |
| [`morphogenesis/experiments/E02_pattern/delta_profile.json`](../morphogenesis/experiments/E02_pattern/delta_profile.json) | other | 1112 | `97de1fe5cf28f2ec7f697c712a887a28295dfcd2f1e61fb4d98fe8705c749fcc` |
| [`morphogenesis/experiments/E02_pattern/gate_layer1.json`](../morphogenesis/experiments/E02_pattern/gate_layer1.json) | other | 17320 | `bf8ce03b8096b5bd4acced0ccaf1355543d9044b1d6d519b2ed348f5b72ad574` |
| [`morphogenesis/experiments/E02_pattern/gate_layer1_attempt1_failed.json`](../morphogenesis/experiments/E02_pattern/gate_layer1_attempt1_failed.json) | other | 7077 | `945d564594e8ebd17d1ed810c58308df84d4da8a694f230ac51b1aa7afd216f2` |
| [`morphogenesis/experiments/E02_pattern/results.json`](../morphogenesis/experiments/E02_pattern/results.json) | other | 268472 | `3a47000b84c4beb6b79ae5e545e4cb11b1ad8ff7e337368ca275b83bfb3a6ef8` |
| [`morphogenesis/experiments/E02_pattern/threshold_probe.json`](../morphogenesis/experiments/E02_pattern/threshold_probe.json) | other | 146978 | `7faaccc67d214a3dfe390dc599910a7afa8ef4d47b37985eb7a197adeca6182d` |
| [`morphogenesis/experiments/E02_pattern/wp4_ablations.json`](../morphogenesis/experiments/E02_pattern/wp4_ablations.json) | other | 863653 | `1c4e8d82c29525793e08887268f81bf1799b19f19aea42e8023cc68f68a71831` |
| [`morphogenesis/experiments/E02_pattern/wp4_reach_probe.json`](../morphogenesis/experiments/E02_pattern/wp4_reach_probe.json) | other | 331138 | `bb575cb38fcca8883483ca1cdbc81bfb68b376366ca894f2d28fe87914e4748d` |
| [`morphogenesis/experiments/E02_pattern/wp4_reach_probe_R9_s1000.json`](../morphogenesis/experiments/E02_pattern/wp4_reach_probe_R9_s1000.json) | other | 110627 | `defc8ee8f29007cf71f3dc78d79c1d27b8427c20d6ff92f72bb88c573a133351` |
| [`morphogenesis/experiments/E02_pattern/wp4_reach_probe_s1000.json`](../morphogenesis/experiments/E02_pattern/wp4_reach_probe_s1000.json) | other | 210622 | `7a2c9be334e1cec500e68e84b4c851591388c3e04a2497a44ecc286d8e52a94f` |
| [`morphogenesis/experiments/E02_pattern/wp4_reach_probe_s2000.json`](../morphogenesis/experiments/E02_pattern/wp4_reach_probe_s2000.json) | other | 99444 | `eb7287b51acbc43250efbae5d9214ae62fbc8dcbfc03ab6b1adced2a77ebd854` |
| [`morphogenesis/experiments/E02b_morphospace/alive_open_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/alive_open_exploratory.json) | experimental | 2846 | `74a183e32b7921026ad1195b364a75190eed0376482383d2581d8397e6086ac3` |
| [`morphogenesis/experiments/E02b_morphospace/asymmetry_sides_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/asymmetry_sides_exploratory.json) | experimental | 1225 | `31e8c13634a3056dc688685712350168c220638b46eaa52317efee6df2e47787` |
| [`morphogenesis/experiments/E02b_morphospace/asymmetry_variance_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/asymmetry_variance_exploratory.json) | experimental | 3445 | `2763f521a9c53248a77943529bd3d0fa152395024a0cd6352f4072bff46f4c48` |
| [`morphogenesis/experiments/E02b_morphospace/asymmetry_variance_retry_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/asymmetry_variance_retry_exploratory.json) | experimental | 2919 | `701d7b06148d32f90c07737da6e1ebe7e89f7b89b8c5b1c28f7e59691c0e9af9` |
| [`morphogenesis/experiments/E02b_morphospace/basin_crossinit_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/basin_crossinit_exploratory.json) | experimental | 33717 | `4b125fa69dcd58be9e750328183c38b111352a5dbb573368433cae1f5191a0f0` |
| [`morphogenesis/experiments/E02b_morphospace/basin_reverse_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/basin_reverse_exploratory.json) | experimental | 23541 | `15468df51c3c7cbe491183db35036b59b291c705ddda81d558762ac46a52829c` |
| [`morphogenesis/experiments/E02b_morphospace/body_integrity_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/body_integrity_exploratory.json) | experimental | 363636 | `73c6bfb976a13d46b21cd4d728913129306e4abba7793597801d7e63a5bb4d6b` |
| [`morphogenesis/experiments/E02b_morphospace/carrier_ch13_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/carrier_ch13_exploratory.json) | experimental | 506 | `2c5017704d49d32f55bf43925554d8d9f9031ce6084736a8a04d96b117c866b0` |
| [`morphogenesis/experiments/E02b_morphospace/carrier_ch15_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/carrier_ch15_exploratory.json) | experimental | 611 | `e41a177d2ff8e15526f2a530e961f464d87ac6af6e70fafa9f6028a7bfea2b20` |
| [`morphogenesis/experiments/E02b_morphospace/carrier_pairs_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/carrier_pairs_exploratory.json) | experimental | 7462 | `279ca0c078b8a83b17b560217cbc6c5e3a540036c0830e39914353186312ce4c` |
| [`morphogenesis/experiments/E02b_morphospace/carriers2_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/carriers2_exploratory.json) | experimental | 7432 | `b413bc0228fd5e41969ef815591d205aa360b64af958da249761e75907e5a9bb` |
| [`morphogenesis/experiments/E02b_morphospace/census.json`](../morphogenesis/experiments/E02b_morphospace/census.json) | canonical | 15526457 | `e81678b603ddc4def4b3c736a4ca0d9b99b2b0b234f666ef620bcae60cad0775` |
| [`morphogenesis/experiments/E02b_morphospace/channel_memory_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/channel_memory_exploratory.json) | experimental | 354495 | `0ca029fb22e2d931e1ef1582336c44852fb847461e0e58ec965a80dd44741b9f` |
| [`morphogenesis/experiments/E02b_morphospace/checkpoint_provenance_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/checkpoint_provenance_exploratory.json) | experimental | 21902 | `983be7ef3b3f13ef30cc8eecb2ebf393ef543bc5e0f6d53dc7a87a5898b16995` |
| [`morphogenesis/experiments/E02b_morphospace/class_centroids_frozen.json`](../morphogenesis/experiments/E02b_morphospace/class_centroids_frozen.json) | canonical | 7310 | `ef71d679a939a089cce6d550b5ea731861ede18161f1cf363972a955e892672d` |
| [`morphogenesis/experiments/E02b_morphospace/closures_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/closures_exploratory.json) | experimental | 20025 | `d3005119a129b93e0b628b1d6d4df62a970914cc73120e730ce8342b8434ed19` |
| [`morphogenesis/experiments/E02b_morphospace/cluster_robustness_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/cluster_robustness_exploratory.json) | experimental | 11245 | `f08b28a89976c1db4183946395f0644f40b1d638382b23ff6bc561626a6238bb` |
| [`morphogenesis/experiments/E02b_morphospace/clusters3_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/clusters3_exploratory.json) | experimental | 7689 | `b832bdd7dc0ff7dd068cc012b15540363f13cd610438fbc05dd03b776686dd3d` |
| [`morphogenesis/experiments/E02b_morphospace/fragment_nucleogenesis_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/fragment_nucleogenesis_exploratory.json) | experimental | 1300734 | `44d13c7f04bd6f294578eccceb32da7564d467394db84e161b8eec7d6ef3b8a6` |
| [`morphogenesis/experiments/E02b_morphospace/generic_class_distance_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/generic_class_distance_exploratory.json) | experimental | 6559 | `1e91157971cc8eb3c26afd735238988fc3aeda02cc3ce08a9a9a02ca10f3dbd9` |
| [`morphogenesis/experiments/E02b_morphospace/geometric_lesion_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/geometric_lesion_exploratory.json) | experimental | 19299 | `28c2e67ce8802b80781b7a2ae8b136937210331859114685ba263d5991dc0570` |
| [`morphogenesis/experiments/E02b_morphospace/geometric_lesion_rep_ema0_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/geometric_lesion_rep_ema0_exploratory.json) | experimental | 267804 | `02aa441b856e8642c41554f5d35ea7a9ca012e6732e68b323491412e2a7edf56` |
| [`morphogenesis/experiments/E02b_morphospace/geometric_lesion_rep_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/geometric_lesion_rep_exploratory.json) | experimental | 275056 | `e45858c7bbd0d5ffff31ffe5818149cfe926e80c27f5ec645b7ca95e2b5c0d45` |
| [`morphogenesis/experiments/E02b_morphospace/geometry_of_form_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/geometry_of_form_exploratory.json) | experimental | 86210 | `d46a02a33f4ca3ca575f4ddd413fd4621c568d05a3663be7c148209841130b6c` |
| [`morphogenesis/experiments/E02b_morphospace/heldout_seeds_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/heldout_seeds_exploratory.json) | experimental | 2506287 | `ca6cac9266117d4150ca29f767ad9b9d65d685c51d363e2644c2e361accc04f9` |
| [`morphogenesis/experiments/E02b_morphospace/left_outcomes_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/left_outcomes_exploratory.json) | experimental | 1728 | `c5ab7a8092710518b2cd74e8cf487209228b2bb43f2269cacb509781b6ccc6ae` |
| [`morphogenesis/experiments/E02b_morphospace/lesion_core_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/lesion_core_exploratory.json) | experimental | 3077 | `8b98088fed85adf08462d2c39170c02868ab8ad4ff7e15ef6fdedc4993b419a9` |
| [`morphogenesis/experiments/E02b_morphospace/lesion_minimal_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/lesion_minimal_exploratory.json) | experimental | 10165 | `7c36af8fed2640e359e1ec8aa9a744109ef9c881283a77490ae3575e96f54a7c` |
| [`morphogenesis/experiments/E02b_morphospace/lesion_necessity_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/lesion_necessity_exploratory.json) | experimental | 1449 | `214098ac99aa2c0cb2a225bb21f08e4edac704da8bcfc53e478917e80f14ea3c` |
| [`morphogenesis/experiments/E02b_morphospace/long_horizon_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/long_horizon_exploratory.json) | experimental | 880833 | `998f2e75712cfb3ce79ded838b295f963a9a4a71575c759e689b5c13a82e3cb5` |
| [`morphogenesis/experiments/E02b_morphospace/patch_identity_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/patch_identity_exploratory.json) | experimental | 16918 | `8a0d5b6e42afe0c6a8b15ebb48c213c2d956a649eb961cd9237ac0e807f4f0d5` |
| [`morphogenesis/experiments/E02b_morphospace/patch_identity_long_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/patch_identity_long_exploratory.json) | experimental | 13509 | `c17158735f2b690df5fc2dd4f76d2aee8f3b4d0e52220a941bcd81322b789a3b` |
| [`morphogenesis/experiments/E02b_morphospace/patch_transplant_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/patch_transplant_exploratory.json) | experimental | 346919 | `903da5908b9256eca342be15098374be519adeddc31a520435e0bb61145bbc34` |
| [`morphogenesis/experiments/E02b_morphospace/perturbations.json`](../morphogenesis/experiments/E02b_morphospace/perturbations.json) | canonical | 1898328 | `64a685acd3ea880b6a21a96518d2c5c6a27105b85177ce284c18d809b0b4125b` |
| [`morphogenesis/experiments/E02b_morphospace/pilot.json`](../morphogenesis/experiments/E02b_morphospace/pilot.json) | other | 595268 | `865b76933a76302cf7ccd0f5d06f5c828d3023274686c7f9e342982f3f6c8701` |
| [`morphogenesis/experiments/E02b_morphospace/prototype_reproducibility_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/prototype_reproducibility_exploratory.json) | experimental | 2556 | `8f512e74259b26e402c59756f71a5b14a5bb3f6e7a383e690335dd66469f8612` |
| [`morphogenesis/experiments/E02b_morphospace/r11_bistability_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/r11_bistability_exploratory.json) | experimental | 36180 | `bcc0e764f2fa187faa494926c20cf13891b2706178fa2623ebd5aecf96f268af` |
| [`morphogenesis/experiments/E02b_morphospace/transient_class_analysis_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/transient_class_analysis_exploratory.json) | experimental | 9109 | `f4822a9074a3c631fee9c36b51914f502e909167b9b3288621bee4015e609172` |
| [`morphogenesis/experiments/E02b_morphospace/transition_matrix_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/transition_matrix_exploratory.json) | experimental | 116121 | `fccc1491477dfc0375bd3ae3b4ccb426b52c558ac7cb37f83a97a888b6164b6a` |
| [`morphogenesis/experiments/E02b_morphospace/transition_matrix_rep_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/transition_matrix_rep_exploratory.json) | experimental | 1051769 | `ecffe71c0d90808b04714df8e3eca019097b76f4396f46bfbc192b7144a57bf7` |
| [`morphogenesis/experiments/E02b_morphospace/untrained_recovery_exploratory.json`](../morphogenesis/experiments/E02b_morphospace/untrained_recovery_exploratory.json) | experimental | 153513 | `90c7ae1845bc7ba5131fe9ed2f3dc9d91dc546386370786e73bdf27943f87bb4` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32long_3000.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32long_3000.json) | derived | 8163693 | `bec1e2fe39545eebf1a8249fb20bb6e3e19bc5264b1d202831873c3bdcccd8ae` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32long_4000.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32long_4000.json) | derived | 10664748 | `2ff97794846e01a63db977d5acec48f3c4d6179852cdb01175bc88862c8bf1bb` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32traj_1000.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32traj_1000.json) | derived | 3872025 | `f56e4c48d3b9daae9e32d53012e7a90e3d8d48273753b4845066ca6d6f9671f2` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32traj_2000.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32traj_2000.json) | derived | 6914095 | `f39c4423444a54d391b8af370fe46789dbeb899bcb88d127ee1afe4af930bcd1` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32traj_3000.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32traj_3000.json) | derived | 9960268 | `35b224766e2f91ad0920276ba666d4f7e5b9f7a1bfde174d67c8ed1f823cf433` |
| [`morphogenesis/experiments/E02c_replication/census_curve_tf32traj_500.json`](../morphogenesis/experiments/E02c_replication/census_curve_tf32traj_500.json) | derived | 2353199 | `16bb0df04e3bcc4a9ecfd648ca0cdba292116acf2052fc14e87d0b7b7718145e` |
| [`morphogenesis/experiments/E02c_replication/census_e02c.json`](../morphogenesis/experiments/E02c_replication/census_e02c.json) | derived | 6379483 | `4450a863259442ac01f061e0db1d848ab55bf9fdbac37f260dc51ea038ed3457` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_data404.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_data404.json) | derived | 3935345 | `df47f9a6d5a22826a5c860d702a8a3972e10a095907bd2370c1b5396480ed85d` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_s4000.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_s4000.json) | derived | 4234871 | `722efd5086a6de956c206ff5b3e1c9e9a81f455ba1f4f6bb35e08121fb8d9904` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed101.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed101.json) | derived | 5574204 | `16fe48bd74a74e3b53f52e3311c4ae5a6e087b035eb36a2d39074c7ad83bf00f` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed202.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed202.json) | derived | 5465247 | `8d0733f8e4f26f78936429b4c36b875d20d3339eac69a29a152f63b6ae7df4f4` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed42.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed42.json) | derived | 4234553 | `e3b8ea079f95e3fa9f66f0e1ddf1b20c551281bb89d0b8500f73d4f2146698c2` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed42_tf32on.json`](../morphogenesis/experiments/E02c_replication/census_e02c_fp32_seed42_tf32on.json) | derived | 4234553 | `1f48cfa321c4d9d1e74c8502e3abacbc8f040b3c4088cd6fb855fd688bce91f2` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_randinit.json`](../morphogenesis/experiments/E02c_replication/census_e02c_randinit.json) | derived | 4235449 | `9d881d346eaffcbf44c1ea4ecc096b7787d39297f8f15779f88d373710101661` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_scan_seed101.json`](../morphogenesis/experiments/E02c_replication/census_e02c_scan_seed101.json) | derived | 6950298 | `6b3d8a10d715764f884788e9a394f6161801776eb13975c75511274fcd3eaf4b` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_seed42repro.json`](../morphogenesis/experiments/E02c_replication/census_e02c_seed42repro.json) | derived | 4047877 | `901de587376f9a70e29028175795bce61f5ebfb9014de28671d9e5d693343383` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_seed42repro_frozen.json`](../morphogenesis/experiments/E02c_replication/census_e02c_seed42repro_frozen.json) | derived | 4234864 | `8ef4394ec7217ad11c85af8a51b11808c600200ef99fa93813a742f01966f776` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_seeddec_A.json`](../morphogenesis/experiments/E02c_replication/census_e02c_seeddec_A.json) | derived | 4064319 | `8f061fb8f23e0f607db385a7601e74b926174c7da2a1e7b6a07f1f85ec00c14f` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_seeddec_B.json`](../morphogenesis/experiments/E02c_replication/census_e02c_seeddec_B.json) | derived | 4235859 | `3c426d984bca80bf230f05a410b1082125652e1abc6592432fb91dfc7efbe645` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_seeddec_wave2.json`](../morphogenesis/experiments/E02c_replication/census_e02c_seeddec_wave2.json) | derived | 8173674 | `54dbc60d3f2da8c2c08d6176ddfe737e8ffe1fd59a8814a4d8e9c8bdd06c4cde` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_tf32_s4000.json`](../morphogenesis/experiments/E02c_replication/census_e02c_tf32_s4000.json) | derived | 3935274 | `5790e6fc7811f5304333f916ff68747de1522e37ff0716e09ea8894f312b0861` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_transient.json`](../morphogenesis/experiments/E02c_replication/census_e02c_transient.json) | derived | 8058795 | `b5fa3a64ef265e3d02874060178549dbbfdce13c55006044336d9ea18959ade3` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_transient_fp32.json`](../morphogenesis/experiments/E02c_replication/census_e02c_transient_fp32.json) | derived | 8323218 | `e5ad20514f96844ef0b08cd4b6993e4676a1f1108eb7f6285dcaeb000f5ee059` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_transient_seed101.json`](../morphogenesis/experiments/E02c_replication/census_e02c_transient_seed101.json) | derived | 8142579 | `50eb019b43f2c35d4c7ceffa4649ceafd2cb5052f613111d644617917eb7117b` |
| [`morphogenesis/experiments/E02c_replication/census_e02c_transient_seed202.json`](../morphogenesis/experiments/E02c_replication/census_e02c_transient_seed202.json) | derived | 8317279 | `db62372c414c7382b92bda8fa4616dccd94c3f08ad0ed2926cfb263a653216ba` |
| [`morphogenesis/experiments/E02c_replication/curve_tf32long.json`](../morphogenesis/experiments/E02c_replication/curve_tf32long.json) | other | 861 | `9cf16bc1f8cadab5953e305761c467f7e198c5662e4c13ea43e12a8de1ee24b4` |
| [`morphogenesis/experiments/E02c_replication/curve_tf32traj.json`](../morphogenesis/experiments/E02c_replication/curve_tf32traj.json) | other | 2074 | `e6cb3015d762162f47de37757357b99f3efdfbd238c440d836d4539527669a24` |
| [`morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s2000_seed42_tf32_boundary.json`](../morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s2000_seed42_tf32_boundary.json) | other | 8150 | `9d83652f35b98ef92bb6f33d4525f66b6402a74a17265f464191d5e7dfb4532a` |
| [`morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s2000_seed42_tf32_randmask.json`](../morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s2000_seed42_tf32_randmask.json) | other | 2678 | `41945049d0dd6430569e62ee187ddefebc8322f6265bd7023e1757e39d428076` |
| [`morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_fp32_boundary.json`](../morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_fp32_boundary.json) | other | 8279 | `306bbec977e4f364f64a912dab4bf0204f13a15d08c1039d65d09eb91b53a8a6` |
| [`morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_tf32_boundary.json`](../morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_tf32_boundary.json) | other | 8092 | `67fa239ad5703e9070283dc0fc26bc20c4314679893d25bc9029e170eb767fe0` |
| [`morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_tf32_randmask.json`](../morphogenesis/experiments/E02c_replication/morphometry_E02c_R-9_s3000_seed42_tf32_randmask.json) | other | 2756 | `82ce1b5820e37051ab690b7a20855e2cd4b065098c269773456aed87eb568297` |
| [`morphogenesis/experiments/E02c_replication/morphometry_holes_sponge101.json`](../morphogenesis/experiments/E02c_replication/morphometry_holes_sponge101.json) | other | 10295 | `afed8cec830d14820faaa6b5253f5e72e1e1aad9220959a6f63260f369e08cec` |
| [`morphogenesis/experiments/E02c_replication/morphometry_holes_sponge42.json`](../morphogenesis/experiments/E02c_replication/morphometry_holes_sponge42.json) | other | 10298 | `a1bed6ce85c104a19b9b9aecaaf91d82e271e60f84c47d587e37fd6e904a51e1` |
| [`morphogenesis/experiments/E02c_replication/randmask_density_020.json`](../morphogenesis/experiments/E02c_replication/randmask_density_020.json) | other | 2681 | `ca3d4c60b822e15df2169de581f3a2e6cc62180488ba3a8d64bbbed4f5112850` |
| [`morphogenesis/experiments/E02c_replication/randmask_density_035.json`](../morphogenesis/experiments/E02c_replication/randmask_density_035.json) | other | 2702 | `2461a223ac4488cec9ee91c1d9eb8bcf295960047626a96ae6d21c388563ba4f` |
| [`morphogenesis/experiments/E02c_replication/randmask_density_050.json`](../morphogenesis/experiments/E02c_replication/randmask_density_050.json) | other | 2683 | `d5498bcac82cece0fac520b4f35adecd26a73feed6fb5524209ba4c91ea94826` |
| [`morphogenesis/experiments/E02c_replication/randmask_density_065.json`](../morphogenesis/experiments/E02c_replication/randmask_density_065.json) | other | 2661 | `81e39b2052dc7bc8baccb3fb470282aa09dff3eb8d02a56c50b59fb18ecad61e` |
| [`morphogenesis/experiments/E02c_replication/randmask_density_080.json`](../morphogenesis/experiments/E02c_replication/randmask_density_080.json) | other | 2678 | `41945049d0dd6430569e62ee187ddefebc8322f6265bd7023e1757e39d428076` |
| [`morphogenesis/experiments/E02c_replication/randmask_du3000_d035.json`](../morphogenesis/experiments/E02c_replication/randmask_du3000_d035.json) | other | 2694 | `a4b9b36ccfbfd9edf1c4dd1602503cef8d232358297d77044b2121e7d1b06f3a` |
| [`morphogenesis/experiments/E02c_replication/randmask_du3000_d065.json`](../morphogenesis/experiments/E02c_replication/randmask_du3000_d065.json) | other | 2681 | `a0e7209933f0f05fbc6d254d5c06b9377562664ee3217ca3c8e73a7140f36874` |
| [`morphogenesis/experiments/E02c_replication/randmask_fp32a_d035.json`](../morphogenesis/experiments/E02c_replication/randmask_fp32a_d035.json) | other | 2652 | `c37f84a359128a14b70613ddcefafefb4759e7ef979525dfc35a52c8ec5db0d0` |
| [`morphogenesis/experiments/E02c_replication/randmask_fp32a_d065.json`](../morphogenesis/experiments/E02c_replication/randmask_fp32a_d065.json) | other | 2613 | `ee2311dcb7db95c0628c0952db3dcf070cfcd4a220b9d24019f4c01d326ec871` |
| [`morphogenesis/experiments/E02c_replication/randmask_s101_2000_d020.json`](../morphogenesis/experiments/E02c_replication/randmask_s101_2000_d020.json) | other | 2392 | `4a095798f1ba96a7bab0fb8605ad37a51dfe46bfc295c4d8a4a7272667d0fa3f` |
| [`morphogenesis/experiments/E02c_replication/randmask_s101_2000_d050.json`](../morphogenesis/experiments/E02c_replication/randmask_s101_2000_d050.json) | other | 2399 | `3424825f3955370de230bff541d808213329d04d8c7f8e062513b6b9b00072ef` |
| [`morphogenesis/experiments/E02c_replication/randmask_s101_2000_d080.json`](../morphogenesis/experiments/E02c_replication/randmask_s101_2000_d080.json) | other | 2390 | `a9c5a5312baf51a5b095e5005cdc799157df364ffb40f716cd0c045d35d5ff8d` |
| [`morphogenesis/experiments/E02c_replication/randmask_sp202_d035.json`](../morphogenesis/experiments/E02c_replication/randmask_sp202_d035.json) | other | 2700 | `94569d3e10478cd7e006edd40353f9f4130be1673db0c922dc61c1a142d49b8b` |
| [`morphogenesis/experiments/E02c_replication/randmask_sp202_d065.json`](../morphogenesis/experiments/E02c_replication/randmask_sp202_d065.json) | other | 2689 | `fb893cdb8a49f0bf3d4a9671a74a04de12222dd997e208ff9f1b1123dcfdb0e1` |
| [`morphogenesis/experiments/E02c_replication/seed_grid.json`](../morphogenesis/experiments/E02c_replication/seed_grid.json) | derived | 6731 | `8ed405953086a5e5186ef2561c3c08bb4c7bf4a3994ac1097929685667881fdb` |
| [`morphogenesis/experiments/E02c_replication/seed_grid_failures.json`](../morphogenesis/experiments/E02c_replication/seed_grid_failures.json) | derived | 1907 | `6fcfd6fabb274f17e980b338ee93611ec1072751babeb1735be0c79592855473` |
| [`morphogenesis/experiments/E02c_replication/signature_curve.json`](../morphogenesis/experiments/E02c_replication/signature_curve.json) | other | 5056 | `dbe6546f4299f102c380d97c4bf82c4a2602807496246cedc19adf6aa20e91d9` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32long_3000.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32long_3000.json) | derived | 3116 | `236f20878e68c823cae7ad789db84a28f7d4c6122b0eac530d6c75ebc64386ed` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32long_4000.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32long_4000.json) | derived | 3116 | `50d7d08fa89e0262be6065b7fbbcd771a4adcdb7fa9caf740ea9b04ba1afed9e` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_1000.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_1000.json) | derived | 3458 | `7cc0de044318c4efb64197aa6b75b769c1d7d9dcdaa3e85f49c86e7167668a3c` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_2000.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_2000.json) | derived | 3458 | `fe992bca9c943861dcf86d5ecb43b1c25261d3d8fada69270d0a794a14b55a95` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_3000.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_3000.json) | derived | 3458 | `0b32a5288a9ddcb83a48bf95e2f57a4b04ec0ae6c9dde0fb8860093acb51b1cc` |
| [`morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_500.json`](../morphogenesis/experiments/E02c_replication/summary_curve_tf32traj_500.json) | derived | 3457 | `d5a95a8f20fe4ef9410c376729277cd3abfd06a144e76c00dfc3fef6679b5be6` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c.json`](../morphogenesis/experiments/E02c_replication/summary_e02c.json) | derived | 2742 | `0bc93846ac23a090eb6109231e7e231750f081d799fe69f7bc47762fc5314e26` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_data404.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_data404.json) | derived | 2590 | `7227661a851e43ad6fbdd5f3f1cd8033fb766fff84167c0b75b419177dd4bbda` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_s4000.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_s4000.json) | derived | 2605 | `88133fc5b342416ecd9d593d9ed35cc58880e10a9315576a6f38fe9138eb5726` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed101.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed101.json) | derived | 3040 | `82e9483351c04af56e8f70d5e94ba5872916d15f005c0c582403cc6ae486599a` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed202.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed202.json) | derived | 3044 | `1d54b289929c3752bd188905db77d94dadeaad49fc01a47b69583ad0e6314cb0` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed42.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed42.json) | derived | 2618 | `7a624c3a74c2815da7116a6b50517fc1ebc4c186edbcaef4a1768070aa5ec733` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed42_tf32on.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_fp32_seed42_tf32on.json) | derived | 2618 | `24e7ecf0ee17a5540399ca471724d9816a93d20dcdc5f46ebd86d6a3e07366a7` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_randinit.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_randinit.json) | derived | 2627 | `3772549c579ed8c443118893337330f4208fd3aacf715747cbfbc0019c03298b` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_scan_seed101.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_scan_seed101.json) | derived | 3468 | `1e24a48eae84c91d97e3bc4eded03c1fc4973f90aa055bf4222aa239e3d8f0b5` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_seed42repro.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_seed42repro.json) | derived | 1619 | `2da80ea3b639284bd4abd903eab6eacd80c24b331a7aaf571ef4642c1b1d689c` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_seed42repro_frozen.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_seed42repro_frozen.json) | derived | 2554 | `5d2a4d02b2ce78a0841dac8224cc72ea9e69d6a37c3b034059075bdd27b19be7` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_A.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_A.json) | derived | 2516 | `9e1c862a871654b53692b21fb979e774f6edacce4a1ce5cb5995550560282674` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_B.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_B.json) | derived | 2531 | `44848130728c4ad20d7fe0c734de8c031e07dffc9333ba2962eded1aae014fc0` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_wave2.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_seeddec_wave2.json) | derived | 4275 | `7abe83504c9b67f4ad166855856b729b2f5fafea777aaa6cff953b907db857e7` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_tf32_s4000.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_tf32_s4000.json) | derived | 2590 | `1e27d3023a005b3c8cfd9e109ff6c6e065252d93fbee80f3b4377faf321d0892` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_transient.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_transient.json) | derived | 3931 | `d465c85d915083e8175a4dbe342c25e3bb2769ea7c26bb6a495b1271dd198c20` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_transient_fp32.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_transient_fp32.json) | derived | 3935 | `7ad3d2a4b9162e9d36231444547726bccfb91dbbd87bd06373700ecd47fadedd` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_transient_seed101.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_transient_seed101.json) | derived | 3950 | `64006558a9a83c9d0be448f72d2f866d2e0020e12a73a9e0da849069f436c797` |
| [`morphogenesis/experiments/E02c_replication/summary_e02c_transient_seed202.json`](../morphogenesis/experiments/E02c_replication/summary_e02c_transient_seed202.json) | derived | 3978 | `f54c93313a2a6bb199649be58815ca5339a6ad4bb333654acd9016aab2ce28bb` |
| [`morphogenesis/experiments/E02c_replication/topology_by_family.json`](../morphogenesis/experiments/E02c_replication/topology_by_family.json) | other | 5913 | `2bd7359434e75de6b146ca5323b517a56f31200f3ec9d4ee8b26fb22034fa695` |
| [`morphogenesis/experiments/E09_pond/drift_matrix.json`](../morphogenesis/experiments/E09_pond/drift_matrix.json) | other | 5145 | `6c5992d368035531f46a4b717d71e5de42249f01393a2b05cf86c302d41ac135` |
| [`morphogenesis/experiments/E09_pond/frequency_matrix.json`](../morphogenesis/experiments/E09_pond/frequency_matrix.json) | other | 16849 | `7fb7d01e66c5b179f519a2af29b6fc0f165dfe2d2f748bd073b4143222b1f46c` |
| [`morphogenesis/experiments/E09_pond/invasion_matrix.json`](../morphogenesis/experiments/E09_pond/invasion_matrix.json) | other | 4940 | `bbc11cbf70aa19690c7f9dd4963ab9dde889ef717730172537033d6988d42ba6` |
| [`morphogenesis/experiments/E09_pond/mobility_matrix.json`](../morphogenesis/experiments/E09_pond/mobility_matrix.json) | other | 11526 | `82b186e9af8678ee255ee5a1824690e72e25c209bd87b9f646b7405c0fecfa85` |
| [`morphogenesis/experiments/E09_pond/organism_mobility_matrix.json`](../morphogenesis/experiments/E09_pond/organism_mobility_matrix.json) | other | 8974 | `7a607e42018b5a1c567a68114fb528e242460f2a252f0e0af1e00f14a78f300a` |
| [`morphogenesis/experiments/E09_pond/pond_ab_p09.json`](../morphogenesis/experiments/E09_pond/pond_ab_p09.json) | other | 124361 | `c6ad2c51d150c7dd8644dc095e9d8f14b01841a5239de34e4cde917ebb3a61a3` |
| [`morphogenesis/experiments/E09_pond/pond_ab_p10.json`](../morphogenesis/experiments/E09_pond/pond_ab_p10.json) | other | 125301 | `8a120b3243f74d2fdd5c6865e7cfc3c0e8f95a193c172018a83355f65a9fcb77` |
| [`morphogenesis/experiments/E09_pond/pond_v01b.json`](../morphogenesis/experiments/E09_pond/pond_v01b.json) | other | 254573 | `b25720c7e2a55d475072181d13bf561da1b61f10244376bdb6aa83bb6069a7bc` |
| [`morphogenesis/experiments/E09_pond/pond_v02_gradient.json`](../morphogenesis/experiments/E09_pond/pond_v02_gradient.json) | other | 211167 | `745bd9d52a42f2407809df9682d77331c154b8fa674b8724ad66b0372ab6ef20` |
| [`morphogenesis/experiments/E09_pond/sense_noise_matrix.json`](../morphogenesis/experiments/E09_pond/sense_noise_matrix.json) | other | 14552 | `f81d9995c5d9b482bfc8d13716f49484e375fc70d1c2fc1c37ebde46cc64c3d7` |
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






















