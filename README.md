# PHISICS Project: Global Continuum Placement

This project is a part of the PHISICS project. It is defined as follows.

## T4.3 Global Continuum Patterns Placement (M4-M30, Leader: RYAX, Participants:ATOS, HUA, BYTE)

This task will be responsible for modelling and deciding on the placement of
the various application components to available and suitable candidate cloud
services and Edge devices. To this end it needs to incorporate aspects such as
performance of the individual services, network links between the service
elements (and/or the request source), cost aspects of the selected services,
legal location constraints, affinity constraints for inter-component
dependencies, energy considerations (based on e.g. available certifications for
a given service, in terms of management or data center/edge resource energy
efficiency). This is the main responsible for deciding on the main interplay
between distribution of components across services and locations, types of
resources , anticipated QoS achieved etc by solving the respective optimization
problem. Various approaches of different scope may be evaluated and balanced ,
e.g. MINLP optimization for optimal selection, evolutionary optimization
approaches for non-optimal but more scalable problem solving, with the ability
to interchange between the main objective to optimize (what aspect e.g. cost or
performance will be the primary scope of optimization) and the remaining
parameters set as constraints. This task receives input from T3.1 regarding the
graph of the application to be deployed, T4.1 regarding the candidate service
types for each component, T4.2 for the evaluated performance and current
condition of each service type. The selected deployment scheme is then
forwarded to T4.5 for the final adaptation and deployment realization.

Roles: The task will be led by RYAX, while ATOS will focus in the modelling
definition and transformation of the decided solution to the platform
specification, linking with T4.5. Partners HUA and BYTE will provide the links
to the respective T3.1, T4.1 and T4.2.T

## Setup

Using docker:
```sh
docker run -ti -p 8080:8080 ryaxtech/global-continuum-placement:main
```

## For development

Install poetry, then run:
```
poetry install
poetry shell
./main.py
```

## Usage

Create a platform file like this one in ./test-platform.json:
```json
{
  "platform": {
    "site1": {
      "type": "Edge",
      "resources": {"nb_cpu": 4, "nb_gpu": 0, "memory_in_MB": 1024},
      "architecture": "x86_64",
      "objective_scores": {"Energy": 60, "Resilience": 5, "Performance": 25}
    },
    "site2": {
      "type": "Edge",
      "resources": {"nb_cpu": 2, "nb_gpu": 1, "memory_in_MB": 4096},
      "architecture": "arm64",
      "objective_scores": {"Energy": 100, "Resilience": 30, "Performance": 50}
    },
    "site3": {
      "type": "HPC",
      "resources": {"nb_cpu": 1000, "nb_gpu": 50, "memory_in_MB": 16e6},
      "objective_scores": {"Energy": 10, "Resilience": 80, "Performance": 100}
    }
  }
}
```
Initialize with a platform description through a REST API:
```sh
curl -H "Content-Type: application/json" -d @test-platform.json http://127.0.0.1:8080/init
```

Create a workload in a file like test-workload.json:

```json
{
  "name": "test",
  "objectives": {
    "Energy": "high",
    "Resilience": "low"
  },
  "tasks": {
    "task1": {
      "resources": {
        "nb_cpu": 1
      },
      "next_tasks": [
        "task2"
      ],
      "constraints": [
        {
          "site": "site3"
        }
      ],
      "architecture": "x86_64"
    },
    "task2": {
      "resources": {
        "nb_cpu": 2
      },
      "next_tasks": [
        "task3",
        "task4"
      ]
    },
    "task3": {
      "resources": {
        "nb_cpu": 2
      }
    },
    "task4": {
      "resources": {
        "nb_cpu": 2
      },
      "next_tasks": [
        "task5"
      ],
      "architecture": "arm64"
    },
    "task5": {
      "resources": {
        "nb_cpu": 2,
        "memory_in_MB": 1000
      }
    }
  }
}
```
Then, we can ask for the scheduler to allocate our workflow tasks on the sites with different constraints:
```sh
curl -H "Content-Type: application/json" -d @test-workload.json http://127.0.0.1:8080/schedule
```

The result is should be:
```json
[
  {
    "task": "task1",
    "site": "site3"
  },
  {
    "task": "task2",
    "site": "site1"
  },
  {
    "task": "task3",
    "site": "site1"
  },
  {
    "task": "task4",
    "site": "site2"
  },
  {
    "task": "task5",
    "site": "site3"
  }
]
```

Let's explain these decisions:
- `task1` has an explicit site constraint for the `site3` so it is allocated there.
- `task2` only requires 2 CPU and all sites have at least 2 CPU. The architecture constraint is not defined but by default it is x86_64, so only the site 1 and 3 can fit the constraint. The scheduler now take into account the objectives and favors the Energy and the Resilience so it choose the `site1`.
- `task3` has the same constraints as `task2` so it goes on the same site, the `site1`because it still has 2 CPU available.
- `task4` goes on `site2` because it requires an `arm64` architecture and only the `site2` is providing it.
- `task5` has only resources constraint and should go to the site1 regarding the objectives but it does not have enough resources. It is finally allocated to `site3` which is the only one that fits the constraints and have available resources.

### Scheduling Algorithm

The scheduling is done task by task in the dependency order of the workflow.

For each task we apply filters to remove sites that do not fit the placement and architecture constraints.
Then, we apply a scoring function based on the objectives scores of the sites and the objective levels of the workflow.
Finally, we use a first fit policy on the sorted by highest score and allocate to the first site in the list that has enough resources.

If not site fits the constraints of a task it is not allocated. (Might be rejected with an error in the future.)

## Development

Setup the environment:
```shell
poetry install
poetry shell
```

In the same terminal run linter with:
```shell
./lint.sh -f
```

Run the tests:
```shell
./test.sh
```



### Add features

1. Write a FAILING test
2. Run it
3. Write the code to make the test pass
4. Lint your code with `./lint.sh -f`
5. Run the tests with `./test.sh`
6. Create a merge request

