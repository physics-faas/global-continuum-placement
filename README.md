# PHYSICS Project: Global Continuum Placement

This code is developed in the context of PHYSICS project to enable the meta-scheduling on a multi-cluster continuum using different algorithms.

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
    "cluster1": {
      "type": "Edge",
      "resources": {"nb_cpu": 4, "nb_gpu": 0, "memory_in_MB": 1024},
      "architecture": "x86_64",
      "objective_scores": {"Energy": 60, "Availability": 5, "Performance": 25}
    },
    "cluster2": {
      "type": "Edge",
      "resources": {"nb_cpu": 2, "nb_gpu": 1, "memory_in_MB": 4096},
      "architecture": "arm64",
      "objective_scores": {"Energy": 100, "Availability": 30, "Performance": 50}
    },
    "cluster3": {
      "type": "HPC",
      "resources": {"nb_cpu": 1000, "nb_gpu": 50, "memory_in_MB": 16e6},
      "objective_scores": {"Energy": 10, "Availability": 80, "Performance": 100}
    }
  }
}
```
Initialize with a platform description through a REST API:
```sh
curl -H "Content-Type: application/json" -d @test-platform.json http://127.0.0.1:8080/clusters
```

Here an example application from the workload-test.json file:
```json
{
  "id": "19fe4293742e0b2c",
  "displayName": "Full example",
  "type": "Flow",
  "executorMode": "NativeSequence",
  "native": true,
  "objectives": {
    "Energy": "high",
    "Availability": "low"
  },
  "flows": [
    {
      "flowID": "flow1",
      "functions": [
        {
          "id": "function1",
          "sequence": 1,
          "allocations": [
            "cluster3"
          ]
        },
        {
          "id": "function2",
          "sequence": 2,
          "annotations": {
            "cores": "2"
          }
        },
        {
          "id": "function3",
          "sequence": 3,
          "annotations": {
            "cores": "2"
          }
        },
        {
          "id": "function4",
          "sequence": 4,
          "annotations": {
            "cores": "2",
            "architecture": "arm64"
          }
        },
        {
          "id": "function5",
          "sequence": 5,
          "annotations": {
            "cores": 2,
            "memory": 1000
          }
        }
      ]
    },
    {
      "flowID": "flow2",
      "executorMode": "NoderedFunction",
      "annotations": {"core": 1, "memory": 1000},
      "functions": [
        {
          "id": "excluded-func",
          "annotations": { }
        }
      ]
    }
  ]
}
```
Then, we can ask for the scheduler to allocate our workflow functions on the clusters with different constraints:
```sh
curl -H "Content-Type: application/json" -d @test-workload.json http://127.0.0.1:8080/applications
```

The result should be:
```json
[
  {
    "flowID": "1234",
    "allocations": [
      {"cluster": "cluster3", "resource_id": "function1"},
      {"cluster": "cluster1", "resource_id": "function2"},
      {"cluster": "cluster1", "resource_id": "function3"},
      {"cluster": "cluster2", "resource_id": "function4"},
      {"cluster": "cluster3", "resource_id": "function5"}
    ]
  },
  {
    "flowID": "flow2",
    "allocations": [
      {"cluster": "cluster1", "resource_id": "flow2"}]
  }
]

```

Let's explain these decisions:
- `function1` has an explicit cluster constraint for the `cluster3` so it is allocated there.
- `function2` only requires 2 CPU and all clusters have at least 2 CPU. The architecture constraint is not defined but by default it is x86_64, so only the cluster 1 and 3 can fit the constraint. The scheduler now take into account the objectives and favors the Energy and the Availability so it choose the `cluster1`.
- `function3` has the same constraints as `function2` so it goes on the same cluster, the `cluster1`because it still has 2 CPU available.
- `function4` goes on `cluster2` because it requires an `arm64` architecture and only the `cluster2` is providing it.
- `function5` has only resources constraint and should go to the cluster1 regarding the objectives but it does not have enough resources. It is finally allocated to `cluster3` which is the only one that fits the constraints and have available resources.
- `flow1`: because it is a NoderedFunction, this flow is scheduled at the flow level. It is scheduled on the `cluster1` because it has enough resources.

This also work at the flow level with the same annotations.

### Scheduling Algorithm

The scheduling is done function by function in the dependency order of the workflow.

For each function we apply filters to remove clusters that do not fit the placement and architecture constraints.
Then, we apply a scoring function based on the objectives scores of the clusters and the objective levels of the workflow.
Finally, we use a first fit policy on the sorted by highest score and allocate to the first cluster in the list that has enough resources.

If not cluster fits the constraints of a function it is not allocated. (Might be rejected with an error in the future.)

#### Foa-Energy scheduling policy

Foa-Energy is an algorithm based on a single-constrained optimization Linear Program, that in addition to extra constraints turns into a multi-objective optimization algorithm.

To take a decision of scheduling, Foa-Energy needs to have access to the platform description, where the different clusters and the number of nodes (or machines) per cluster are available. As a direct inputs, Foa-Energy needs to receive, per cluster (these inputs are provided into the workload json file):
- `"averageDuration"`: 5.36,
- `"averageDurationContainer"`: 1,
- `"averageEnergy"`: 1,
- `"averageEnergyContainer"`: 1,

Foa-Energy follows a few notations:
- `p`: Functions' execution time -> "averageDuration"
- `p_tilde`: Containers' execution time -> "averageDurationContainer" -> 
- `c`: Functions' energy consumption -> "averageEnergy"
- `c_tilde`: Containers' energy consumption -> "averageEnergyContainer"
- `N`: The number of functions in the batch
- `H`: Number of clusters available
- `K`: Number of different containers used
- `env`: The association of container and function
- `mc`: The number of machines per cluster
- `TMax`: A constraint of makespan (maximum execution time)
- `CMax`: A constraint of amount of data downloaded for containers

The solution will be proposed as matrix `x` and `y`, where `x` is the allocation of functions over the clusters, and `y` the allocation of containers over the clusters.
For a local level of scheduling, it is needed an algorithm to takes Foa-Energy decisions and to do the local placement.

For more details, please refer to [Foa-Energy's paper repository][https://gitlab.com/andersonandrei/foa-energy-journal]

## Supported annotations

for now the component supports these annotations:
- `cores` : number of CPU cores
- `memory` : memory in MB
- `locality` : which is a cluster type defines for each cluster like "HPC", "Cloud", "Edge", and "On-premise".
- `architecture`: Hardware architecture, one of "x86_64", "arm64" 
- `optimizationGoal`: Should be "Energy", "Performance", or "Availability"
- `importance`:  the level associated to this goal : "Low, "Medium", "High"

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

