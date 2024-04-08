![Tests](https://github.com/PlatypusBytes/ROSE-dashboard/actions/workflows/workflow.yml/badge.svg)

# Dashboard for ROSE
This is the repository for the [ROSE-model](https://github.com/PlatypusBytes/ROSE) dashboard.

![ROSE Dashboard Demo](/_static/dashboard.gif)

# How to run
In order to run the dashboard, first you need to install the ROSE-dashboard package.
You can do this by running the following command (we recommend to install the dashboard in a virtual environment
to avoid conflicts with other packages):

```bash
pip install git+https:\\github.com\PlatypusBytes\ROSE-dashboard.git
```

The dashboard is build with Flask. To run the dashboard you need to set the an environment variable _FLASK_APP_.
This can be done by running the following commands:

```bash
export FLASK_APP=dashboard:create_app
```

To run the dashboard you can now use the following command:

```bash
flask run
```

Go to your web browser and navigate to: http://localhost:5000/ in your web browser.
