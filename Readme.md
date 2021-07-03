![Bames](img/Logo.jpg)
A stupid engine to play games on a Beamer.

Written in python 3.7.

# Architecture
## Parsing and Distorting
* `Bame` creates a `Barser`
* The `Barser` then creates a process which runs the `BictureTaker` and afterwards the `BarserEmployees` supplied by the Game-Instance.
