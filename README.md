# ZKarel

A Karel like environment for learning programming
fundamentals. Currently supports the following programming languages.

  * Python
  * C

## Installing ZKarel

To install from source, the instructions are provided below.

	$ make
	$ pip install --user .

## Using ZKarel

ZKarel has a Karel simulator application that displays the world, and
position of Karel in the world. The user can choose the world from the
Karel simulator application menu. The Karel simulator application can
be started using the following command.

	$ karel-sim

The user can then create a workspace for writing programs to control
Karel using the following command.

	$ karel-init <lang>

The currently supported values for `lang` are `python` and `clang`.

## Karel API

  * `start()` - starts Karel, should be called before any other command
  * `stop()` - stops Karel, should be called after all commands are completed
  * `move()` - moves Karel one step forward
  * `turn_left()` - turns Karel to the left
  * `pick_beeper()` - picks one beeper from the current position, and
    places in beeper bag
  * `put_beeper()` - puts one beeper from the beeper bag, at the
    current position
  * `front_is_clear()` - returns true if there is no wall in the front
  * `left_is_clear()` - returns true if there is no wall in the left
  * `right_is_clear()` - returns true if there is no wall in the right
  * `beeper()` - returns true if there is a beeper at the current position
  * `next_to_a_beeper()` - same as `beeper()`
  * `facing_north()` - returns true if Karel is facing north
  * `facing_south()` - returns true if Karel is facing south
  * `facing_east()` - returns true if Karel is facing east
  * `facing_west()` - returns true if Karel is facing west
  * `any_beepers_in_beeper_bag()` - returns true if there are beepers in beeper bag
  * `gpsx()` - returns Karel's X position
  * `avenue()` - same as `gpsx()`
  * `gpsy()` - returns Karel's Y position
  * `street()` - same as `gpsy()`

