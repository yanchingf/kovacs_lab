
Benchmarking n=10 (k_neighbors=None) ...
  search:        0.004 ms
  smart_search:  0.010 ms
  decimate:      0.021 ms
  smart_decimate:0.029 ms
  repair:        0.260 ms
  repair_scoped: 0.954 ms
Benchmarking n=25 (k_neighbors=None) ...
  search:        0.006 ms
  smart_search:  0.052 ms
  decimate:      0.037 ms
  smart_decimate:0.070 ms
  repair:        0.882 ms
  repair_scoped: 2.149 ms
Benchmarking n=50 (k_neighbors=None) ...
  search:        0.014 ms
  smart_search:  0.139 ms
  decimate:      0.093 ms
  smart_decimate:0.201 ms
  repair:        5.416 ms
  repair_scoped: 5.158 ms
Benchmarking n=100 (k_neighbors=None) ...
  search:        0.026 ms
  smart_search:  0.616 ms
  decimate:      0.143 ms
  smart_decimate:0.350 ms
  repair:        17.583 ms
  repair_scoped: 12.261 ms
Benchmarking n=200 (k_neighbors=None) ...
  search:        0.029 ms
  smart_search:  1.844 ms
  decimate:      0.189 ms
  smart_decimate:0.969 ms
  repair:        153.957 ms
  repair_scoped: 35.949 ms
Benchmarking n=300 (k_neighbors=None) ...
  search:        0.092 ms
  smart_search:  3.559 ms
  decimate:      0.204 ms
  smart_decimate:10.387 ms
  repair:        317.423 ms
  repair_scoped: 73.674 ms
Benchmarking n=400 (k_neighbors=None) ...
  search:        0.086 ms
  smart_search:  6.787 ms
  decimate:      0.385 ms
  smart_decimate:14.331 ms
  repair:        465.732 ms
  repair_scoped: 77.159 ms
Benchmarking n=1000 (k_neighbors=None) ...
  search:        0.205 ms
  smart_search:  42.976 ms
  decimate:      0.837 ms
  smart_decimate:30.451 ms
  repair:        2886.839 ms
  repair_scoped: 287.585 ms
Benchmarking n=2500 (k_neighbors=None) ...
  search:        0.406 ms
  smart_search:  229.668 ms
  decimate:      1.649 ms
  smart_decimate:230.788 ms
  repair:        17878.093 ms
  repair_scoped: 1401.068 ms

Saved plot to c:\Users\milan\Desktop\SURG_2026\src\..\tests\test-plots\runtime_scaling_k=None.png

Summary (ms):
     n     search   decimate     repair  repair_scoped  smart_search  smart_decimate
    10      0.004      0.021      0.260          0.954         0.010           0.029
    25      0.006      0.037      0.882          2.149         0.052           0.070
    50      0.014      0.093      5.416          5.158         0.139           0.201
   100      0.026      0.143     17.583         12.261         0.616           0.350
   200      0.029      0.189    153.957         35.949         1.844           0.969
   300      0.092      0.204    317.423         73.674         3.559          10.387
   400      0.086      0.385    465.732         77.159         6.787          14.331
  1000      0.205      0.837   2886.839        287.585        42.976          30.451
  2500      0.406      1.649  17878.093       1401.068       229.668         230.788
Benchmarking n=10 (k_neighbors=5) ...
  search:        0.018 ms
  smart_search:  0.078 ms
  decimate:      0.046 ms
  smart_decimate:0.094 ms
  repair:        0.092 ms
  repair_scoped: 2.606 ms
Benchmarking n=25 (k_neighbors=5) ...
  search:        0.009 ms
  smart_search:  0.124 ms
  decimate:      0.043 ms
  smart_decimate:0.207 ms
  repair:        1.881 ms
  repair_scoped: 3.660 ms
Benchmarking n=50 (k_neighbors=5) ...
  search:        0.011 ms
  smart_search:  0.165 ms
  decimate:      0.070 ms
  smart_decimate:0.209 ms
  repair:        8.561 ms
  repair_scoped: 7.358 ms
Benchmarking n=100 (k_neighbors=5) ...
  search:        0.041 ms
  smart_search:  0.543 ms
  decimate:      0.189 ms
  smart_decimate:0.377 ms
  repair:        26.937 ms
  repair_scoped: 16.964 ms
Benchmarking n=200 (k_neighbors=5) ...
  search:        0.042 ms
  smart_search:  2.130 ms
  decimate:      0.151 ms
  smart_decimate:0.755 ms
  repair:        109.655 ms
  repair_scoped: 39.757 ms
Benchmarking n=300 (k_neighbors=5) ...
  search:        0.031 ms
  smart_search:  0.976 ms
  decimate:      0.185 ms
  smart_decimate:1.113 ms
  repair:        239.576 ms
  repair_scoped: 77.675 ms
Benchmarking n=400 (k_neighbors=5) ...
  search:        0.076 ms
  smart_search:  2.313 ms
  decimate:      0.311 ms
  smart_decimate:1.541 ms
  repair:        498.761 ms
  repair_scoped: 110.967 ms
Benchmarking n=1000 (k_neighbors=5) ...
  search:        0.215 ms
  smart_search:  3.424 ms
  decimate:      0.659 ms
  smart_decimate:4.264 ms
  repair:        3018.626 ms
  repair_scoped: 459.726 ms
Benchmarking n=2500 (k_neighbors=5) ...
  search:        0.237 ms
  smart_search:  15.579 ms
  decimate:      3.365 ms
  smart_decimate:9.703 ms
  repair:        15482.196 ms
  repair_scoped: 2201.055 ms

Saved plot to c:\Users\milan\Desktop\SURG_2026\src\..\tests\test-plots\runtime_scaling_k=5.png

Summary (ms):
     n     search   decimate     repair  repair_scoped  smart_search  smart_decimate
    10      0.018      0.046      0.092          2.606         0.078           0.094
    25      0.009      0.043      1.881          3.660         0.124           0.207
    50      0.011      0.070      8.561          7.358         0.165           0.209
   100      0.041      0.189     26.937         16.964         0.543           0.377
   200      0.042      0.151    109.655         39.757         2.130           0.755
   300      0.031      0.185    239.576         77.675         0.976           1.113
   400      0.076      0.311    498.761        110.967         2.313           1.541
  1000      0.215      0.659   3018.626        459.726         3.424           4.264
  2500      0.237      3.365  15482.196       2201.055        15.579           9.703
Benchmarking n=10 (k_neighbors=10) ...
  search:        0.006 ms
  smart_search:  0.026 ms
  decimate:      0.030 ms
  smart_decimate:0.126 ms
  repair:        0.037 ms
  repair_scoped: 1.279 ms
Benchmarking n=25 (k_neighbors=10) ...
  search:        0.007 ms
  smart_search:  0.137 ms
  decimate:      0.052 ms
  smart_decimate:0.298 ms
  repair:        1.263 ms
  repair_scoped: 3.469 ms
Benchmarking n=50 (k_neighbors=10) ...
  search:        0.017 ms
  smart_search:  0.343 ms
  decimate:      0.093 ms
  smart_decimate:0.459 ms
  repair:        6.611 ms
  repair_scoped: 7.361 ms
Benchmarking n=100 (k_neighbors=10) ...
  search:        0.018 ms
  smart_search:  0.432 ms
  decimate:      0.089 ms
  smart_decimate:0.531 ms
  repair:        20.233 ms
  repair_scoped: 13.166 ms
Benchmarking n=200 (k_neighbors=10) ...
  search:        0.039 ms
  smart_search:  1.529 ms
  decimate:      0.278 ms
  smart_decimate:0.995 ms
  repair:        84.330 ms
  repair_scoped: 40.736 ms
Benchmarking n=300 (k_neighbors=10) ...
  search:        0.120 ms
  smart_search:  1.697 ms
  decimate:      0.226 ms
  smart_decimate:1.769 ms
  repair:        223.122 ms
  repair_scoped: 57.093 ms
Benchmarking n=400 (k_neighbors=10) ...
  search:        0.066 ms
  smart_search:  2.966 ms
  decimate:      0.215 ms
  smart_decimate:1.976 ms
  repair:        408.462 ms
  repair_scoped: 86.394 ms
Benchmarking n=1000 (k_neighbors=10) ...
  search:        0.158 ms
  smart_search:  5.026 ms
  decimate:      0.568 ms
  smart_decimate:5.238 ms
  repair:        2497.135 ms
  repair_scoped: 400.707 ms
Benchmarking n=2500 (k_neighbors=10) ...
  search:        0.206 ms
  smart_search:  19.013 ms
  decimate:      1.879 ms
  smart_decimate:13.992 ms
  repair:        16403.600 ms
  repair_scoped: 4114.916 ms

Saved plot to c:\Users\milan\Desktop\SURG_2026\src\..\tests\test-plots\runtime_scaling_k=10.png

Summary (ms):
     n     search   decimate     repair  repair_scoped  smart_search  smart_decimate
    10      0.006      0.030      0.037          1.279         0.026           0.126
    25      0.007      0.052      1.263          3.469         0.137           0.298
    50      0.017      0.093      6.611          7.361         0.343           0.459
   100      0.018      0.089     20.233         13.166         0.432           0.531
   200      0.039      0.278     84.330         40.736         1.529           0.995
   300      0.120      0.226    223.122         57.093         1.697           1.769
   400      0.066      0.215    408.462         86.394         2.966           1.976
  1000      0.158      0.568   2497.135        400.707         5.026           5.238
  2500      0.206      1.879  16403.600       4114.916        19.013          13.992
Full-run benchmarking n=10 (k_neighbors=None) ...
  naive: 0.52 ms over 10 steps
  smart: 0.45 ms over 10 steps
Full-run benchmarking n=25 (k_neighbors=None) ...
  naive: 2.75 ms over 25 steps
  smart: 2.32 ms over 25 steps
Full-run benchmarking n=50 (k_neighbors=None) ...
  naive: 8.96 ms over 50 steps
  smart: 12.08 ms over 50 steps
Full-run benchmarking n=100 (k_neighbors=None) ...
  naive: 23.81 ms over 100 steps
  smart: 33.90 ms over 100 steps
Full-run benchmarking n=200 (k_neighbors=None) ...
  naive: 81.51 ms over 200 steps
  smart: 362.84 ms over 200 steps
Full-run benchmarking n=300 (k_neighbors=None) ...
  naive: 205.48 ms over 300 steps
  smart: 1105.94 ms over 300 steps
Full-run benchmarking n=400 (k_neighbors=None) ...
  naive: 326.03 ms over 400 steps
  smart: 2312.81 ms over 400 steps
Full-run benchmarking n=1000 (k_neighbors=None) ...
  naive: 1782.29 ms over 1000 steps
  smart: 36797.54 ms over 1000 steps

Saved plot to c:\Users\milan\Desktop\SURG_2026\src\..\tests\test-plots\full_run_dense.png
Full-run benchmarking n=10 (k_neighbors=5) ...
  naive: 0.29 ms over 10 steps
  smart: 0.39 ms over 10 steps
Full-run benchmarking n=25 (k_neighbors=5) ...
  naive: 3.51 ms over 25 steps
  smart: 5.51 ms over 25 steps
Full-run benchmarking n=50 (k_neighbors=5) ...
  naive: 5.75 ms over 50 steps
  smart: 15.95 ms over 50 steps
Full-run benchmarking n=100 (k_neighbors=5) ...
  naive: 15.10 ms over 100 steps
  smart: 50.09 ms over 100 steps
Full-run benchmarking n=200 (k_neighbors=5) ...
  naive: 102.24 ms over 200 steps
  smart: 233.83 ms over 200 steps
Full-run benchmarking n=300 (k_neighbors=5) ...
  naive: 174.80 ms over 300 steps
  smart: 503.53 ms over 300 steps
Full-run benchmarking n=400 (k_neighbors=5) ...
  naive: 309.42 ms over 400 steps
  smart: 915.90 ms over 400 steps
Full-run benchmarking n=1000 (k_neighbors=5) ...
  naive: 2085.25 ms over 1000 steps
  smart: 5643.78 ms over 1000 steps

Saved plot to c:\Users\milan\Desktop\SURG_2026\src\..\tests\test-plots\full_run_k=5.png
Full-run benchmarking n=10 (k_neighbors=10) ...
  naive: 0.37 ms over 10 steps
  smart: 0.62 ms over 10 steps
Full-run benchmarking n=25 (k_neighbors=10) ...
  naive: 1.29 ms over 25 steps
  smart: 4.88 ms over 25 steps
Full-run benchmarking n=50 (k_neighbors=10) ...
  naive: 5.36 ms over 50 steps
  smart: 21.48 ms over 50 steps
Full-run benchmarking n=100 (k_neighbors=10) ...
  naive: 16.60 ms over 100 steps
  smart: 54.24 ms over 100 steps
Full-run benchmarking n=200 (k_neighbors=10) ...
  naive: 70.41 ms over 200 steps
  smart: 211.82 ms over 200 steps
Full-run benchmarking n=300 (k_neighbors=10) ...
  naive: 199.57 ms over 300 steps
  smart: 502.47 ms over 300 steps
Full-run benchmarking n=400 (k_neighbors=10) ...
  naive: 279.00 ms over 400 steps
  smart: 944.23 ms over 400 steps
Full-run benchmarking n=1000 (k_neighbors=10) ...
  naive: 1597.64 ms over 1000 steps
  smart: 4998.03 ms over 1000 steps
