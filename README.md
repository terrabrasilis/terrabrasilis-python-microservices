# TerraBrasilis microservices based in Python
The purpose of this project is provide some common modules and a simple template for build microservices based in Python and Docker.

## Developer

This repository is developed using Python 3.5 so we recomend that you use a virtual environment for prepare your dev environment.

- First all you should clone repository
- Them enter into the created directory
- Create the virtual environment for Python

```sh
sudo apt-get install python3-venv
python3 -m venv env
```

- Active the virtual environment

```sh
source env/bin/activate
```

- Install the packages using pip and the requirements.txt for modules that you need for your service.


# For a new service

After create your own code, use the pip freezy to generate the requerimets.txt to provide the easy reproduction of run on other environment or build the docker image.

Command to generate
```sh
pip freeze > requirements.txt
```

Command to install from requirements
```sh
pip install -r requirements.txt
```