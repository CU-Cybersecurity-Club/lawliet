# Lawliet

[![Build Status](https://travis-ci.com/CU-Cybersecurity-Club/lawliet.svg?branch=master)](https://travis-ci.com/CU-Cybersecurity-Club/lawliet)
[![codecov](https://codecov.io/gh/CU-Cybersecurity-Club/lawliet/branch/master/graph/badge.svg)](https://codecov.io/gh/CU-Cybersecurity-Club/lawliet)

The universal lab environment deployment system.

## What's Lawliet?
Lawliet is a system for quickly creating and deploying lab environments. It is similar to [JupyterHub](https://jupyter.org/hub), and in fact can largely replicate JupyterHub's functionality by deploying Jupyter Notebook servers very easily. However, Lawliet's functionality is meant to be a strict superset of JupyterHub's in that it can deploy a much, much wider variety of environments than just Jupyter Notebooks.

## What motivated this project?
This project was started by members of the leadership for the [CU Cybersecurity Club](https://cucybersecurityclub.com) at the University of Colorado Boulder. Over time, as the Cyber Club has tried to teach hands-on workshops and started teams for security competitions (which entails preparing labs to teach newer team members various concepts), we've noticed a few patterns:

- Students have difficulty installing software themselves due to complicated installation instructions, large downloads, and so on.
- Creating training materials is very time-consuming, especially if you want to hit a wide variety of topics at multiple skill levels.

To solve these problems, we started to create some virtualized environments that gave students access to all of the tools and learning materials that they needed. But this came with its own problems:

- There isn't an easy way to provide students with access to most kinds of environments we'd be interested in (e.g. desktops).
- It's even harder to spawn groups of machines that have to interact with each other (a pre-requisite for us to run attack-defend exercises and certain kinds of CTFs).
- We need a way to automate deployment of lab environments for large groups of students.

We developed Lawliet as our solution to these problems. Lawliet uses Kubernetes to spawn and import new labs, and to scale up and down for the number of users we have at a given time. It provides a web interface for accessing lab environments, so that all students need to get up and running is a browser.
