from numpy import array
from pulp import (
    GUROBI_CMD,
    PULP_CBC_CMD,
    LpMinimize,
    LpProblem,
    LpStatus,
    LpVariable,
    lpSum,
    value,
)


def lp_energy(N, H, K, c, p, c_tilde, p_tilde, mc, env, Tmax, solver, verbose):

    x = LpVariable.dicts("x_", (H, N), 0, cat="Binary")  # dimension nxh
    y = LpVariable.dicts("y_", (H, K), 0, cat="Binary")  # e in the LP, dimension kxh

    prob = LpProblem("myProblem", LpMinimize)

    # 3
    for i in N:
        prob.addConstraint(lpSum([x[h][i] for h in H]) >= 1)

    # 4
    for h in H:
        prob.addConstraint(
            (
                lpSum([p[h][i] * x[h][i] for i in N])
                + lpSum([p_tilde[h][k] * y[h][k] for k in K])
            )
            <= mc[h] * Tmax
        )

    # 5
    for h in H:
        for k in K:
            task_per_env = [i_env for i_env in N if env[i_env] == k]
            if len(task_per_env) != 0:
                prob.addConstraint(
                    (
                        lpSum([p[h][i] * x[h][i] for i in task_per_env])
                        - y[h][k] * (Tmax - p_tilde[h][k])
                    )
                    <= 0
                )

    prob += lpSum([c[h][i] * x[h][i] for i in N] for h in H) + lpSum(
        [c_tilde[h][k] * y[h][k] for k in K] for h in H
    )

    solution_x = [[0 for col in H] for row in N]
    solution_y = [[0 for col in H] for row in K]

    if solver == "CBC":
        if verbose == 1:
            status = prob.solve(PULP_CBC_CMD())
        else:
            status = prob.solve(PULP_CBC_CMD(msg=0))
    else:
        if verbose == 1:
            status = prob.solve(GUROBI_CMD())
        else:
            status = prob.solve(GUROBI_CMD(msg=0))

    print(LpStatus[status])
    print("Value ", value(prob.objective))
    print("Status: ", status)
    # print(prob.constraints())

    for v in prob.variables():
        solution_var = v.name.split("_")[0]
        index_i = int(v.name.split("_")[-1])
        index_j = int(v.name.split("_")[-2])

        if solution_var == "x":
            solution_x[index_i][index_j] = v.varValue
        else:
            solution_y[index_i][index_j] = v.varValue

    solution_x = array(solution_x)
    solution_y = array(solution_y)

    return solution_x, solution_y
