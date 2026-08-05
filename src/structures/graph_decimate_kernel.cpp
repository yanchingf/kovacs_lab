
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <omp.h>
#include <vector>

namespace py = pybind11;

py::tuple search_kernel(py::array_t<double> adj, py::array_t<double> ranges, py::array_t<bool> active, int n)

{
    auto adj_buf = adj.unchecked<2>();
    auto range_buf = ranges.unchecked<1>();
    auto active_buf = active.unchecked<1>();

    // Pass 1: parallel scan for a mutual in-range bond
    int found_i = -1, found_j = -1;

    #pragma omp parallel for schedule(dynamic)
    for (int i = 0; i < n; i++) {
        if (!active_buf(i)) continue;
        if (found_i != -1) continue;
        for (int j = 0; j < n; j++) {
            if (i == j || !active_buf(j)) continue;
            double d = adj_buf(i, j);
            if (d > 0 && d <= range_buf(i) && d <= range_buf(j)) {
                #pragma omp critical
                {
                    if (found_i == -1) { 
                        found_i = i; 
                        found_j = j; 
                    }
                }
            }
        }
    }

    if (found_i != -1) {
        return py::make_tuple(found_i, found_j);
    }

    // Pass 2: parallel can_reach 
    int best = -1, best_degree = INT32_MAX;

    #pragma omp parallel
    {
        int local_best = -1, local_best_degree = INT32_MAX;

        #pragma omp for schedule(dynamic)
        for (int i = 0; i < n; i++) {
            if (!active_buf(i)) continue;
            bool can_reach = false;
            int degree = 0;
            for (int j = 0; j < n; j++) {
                if (i == j || !active_buf(j)) continue;
                double d = adj_buf(i, j);
                if (d > 0) degree++;
                if (d > 0 && d <= range_buf(i)) can_reach = true;
            }
            if (!can_reach && degree < local_best_degree) {
                local_best = i;
                local_best_degree = degree;
            }
        }

        #pragma omp critical
        {
            if (local_best != -1 && local_best_degree < best_degree) {
                best = local_best;
                best_degree = local_best_degree;
            }
        }
    }

    if (best != -1) return py::make_tuple(best, py::none());
    return py::make_tuple(py::none(), py::none());
}

PYBIND11_MODULE(graph_decimate_kernel, m) {
    m.def("search_kernel", &search_kernel, "Parallel SDRG search");
}