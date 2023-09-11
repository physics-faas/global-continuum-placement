#! /bin/sh

curl -H "Content-Type: application/json" -d @test-platform.json http://127.0.0.1:8080/clusters
curl -H "Content-Type: application/json" -d @test-workload.json http://127.0.0.1:8080/applications
