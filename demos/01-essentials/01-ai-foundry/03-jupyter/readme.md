# Introduction to Jupyter Notebooks

[Jupyter Notebooks](https://jupyter.org/) are an open-source web application that allows you to create and share documents that contain live code, equations, visualizations, and narrative text. They are widely used in data cleaning and transformation, numerical simulation, statistical modeling, data visualization, machine learning, and much more.. They are using the `*.ipynb` file extension.

## Installation

>Note: You might have to create a new virtual environment for this quick start.

- You can install Jupyter Notebook via pip:

    ```bash
    pip install notebook
    ```

## Starting a Jupyter Notebook

- To start a Jupyter Notebook, you can use the following command in your terminal:

    ```bash
    jupyter notebook
    ```

- This will open a new page in your web browser with your current directory.

    ![jupyter](_images/jupyter-notebooks.jpg)


## Creating a New Notebook

- To create a new notebook, click on the "New" button and select "Python 3" (or the version you have installed).

    ![create-notebook](_images/create-notebook.jpg)


## Cells

Jupyter notebook consists of cells. Each cell can contain code, text, or images. You can run each cell individually. The output of one cell can be used as input for another cell.

- Here is a basic example of a cell in a Jupyter Notebook:

    ```bash
    # This is a comment in a Jupyter Notebook cell
    print("Hello, World!")
    ```

- To run the cell, you can press Shift + Enter.

