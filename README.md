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

TODO: Details about development environment setup.

## Development

1. Write a FAILING test
2. Run it
3. Write the code to make the test pass
4. Lint your code with `./lint.sh -f`
5. Run the tests with `./test.sh`
6. Create a merge request

