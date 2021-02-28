<div align="center">
  <img src="https://github.com/zachoooo/ex.py/raw/main/assets/logo.png">

  ex.py helps you make Google Sheets (and Excel) formulas more easily!
  
  [![Contributors][contributors-shield]][contributors-url]
  [![Forks][forks-shield]][forks-url]
  [![Stargazers][stars-shield]][stars-url]
  [![Issues][issues-shield]][issues-url]
  [![License][license-shield]][license-url]</center>
</div>

## About

If you ever tried writing formulas in Google Sheets, you know it can get messy real quick. While Excel lets you declare variables using the Name Manager, Google Sheets does not. This means that formulas can become dense and barely readable really quickly.

Let's take a simple example. Let's say you asked a child in elementary school to record the ages and heights of all their friends and their parents. They get the data back to you in Google Sheets. You don't really care if the kid measured accurrately, but you do want to ensure that they measured consistently. To do this, you want to compare the average heights of everyone under 12 with everyone over 12. If they measured consistently, then the adults should be about 26 centimeters taller than the children on average.

You need to create a single function that will tell you if the data they entered is consistent with what you expect. You have a class of 50 kids, so you don't want to spend all day naming ranges, copying formulas, and pasting them into a bunch of cells. You need ONE formula for each student spreadsheet. The formula should first check to make sure that they have a certain minimum number of entries in their data. If they don't have enough entries, then the formula should output `"INSUFFICIENT ENTRIES"`. If they do meet that minimum threshold, then the formula should calculate the average height of everyone over 12 years old and the average height of everyone at or under 12 years old. It should then calculate the difference between these averages. You know what the average distance should be and the formula should then tell you whether or not their values are `"Expected"`, `"Unexpected"`, or `"Extreme"` based on specific threshold values. If the value is `"Expected"` then the formula should just output `"Expected"`. If it is `"Unexpected"` or `"Extreme"` then the formula should output the label followed by the difference in averages between the two age groups like this `"Unexpected: 15"`.

So you sit down with your formulas and after 3 straight hours of trial and error you get this:

```
=IF(NOT(AND(COUNTA(C2:C1000)-COUNTIF(B2:B1000,"<=12")>=1,COUNTIF(B2:B1000,"<=12")>=1)),"INSUFFICIENT DATA",IF(NOT(AND(AVERAGEIFS(C2:C1000,B2:B1000,">12")-AVERAGEIFS(C2:C1000,B2:B1000,"<=12")<31,AVERAGEIFS(C2:C1000,B2:B1000,">12")-AVERAGEIFS(C2:C1000,B2:B1000,"<=12")>21)),IF(OR(AVERAGEIFS(C2:C1000,B2:B1000,">12")-AVERAGEIFS(C2:C1000,B2:B1000,"<=12")>36,AVERAGEIFS(C2:C1000,B2:B1000,">12")-AVERAGEIFS(C2:C1000,B2:B1000,"<=12")<10),IF(AND(AVERAGEIFS(C2:C1000,B2:B1000,">12")-AVERAGEIFS(C2:C1000,B2:B1000,"<=12")<31,AVERAGEIFS(C2:C1000,B2:B1000,">12")-AVERAGEIFS(C2:C1000,B2:B1000,"<=12")>21),"Expected","Extreme"),"Unexpected")&" Difference: "&AVERAGEIFS(C2:C1000,B2:B1000,">12")-AVERAGEIFS(C2:C1000,B2:B1000,"<=12"),IF(OR(AVERAGEIFS(C2:C1000,B2:B1000,">12")-AVERAGEIFS(C2:C1000,B2:B1000,"<=12")>36,AVERAGEIFS(C2:C1000,B2:B1000,">12")-AVERAGEIFS(C2:C1000,B2:B1000,"<=12")<10),IF(AND(AVERAGEIFS(C2:C1000,B2:B1000,">12")-AVERAGEIFS(C2:C1000,B2:B1000,"<=12")<31,AVERAGEIFS(C2:C1000,B2:B1000,">12")-AVERAGEIFS(C2:C1000,B2:B1000,"<=12")>21),"Expected","Extreme"),"Unexpected")))
```

This works great for your example spreadsheet, but once you get student submissions, you realize somethings wrong. The formula works fine for centiemeters, but a third of your class used inches and another third used the length of their arm to measure! This isn't going to work anymore! You need to rewrite this to use the proportion of average heights, not raw centimeter values. It's been a couple days since you last looked at this formula and it is complete gibberish at this point. You give up, not willing to expend the energy to tackle this monstrosity. This is exactly where ex.py can help!

With ex.py, you get the much more comprehensible code of:

```python
ages = B2:B1000
heights = C2:C1000

num_under_12 = COUNTIF(ages, "<=12")
num_over_12 = COUNTA(heights) - num_under_12
is_data_sufficient = AND(num_over_12 >= 1, num_under_12 >= 1)

avg_over_12 = AVERAGEIFS(heights, ages, ">12")
under_12_avg = AVERAGEIFS(heights, ages, "<=12")
avg_dif = avg_over_12 - under_12_avg

is_extreme = OR(avg_dif > 36, avg_dif < 10)
is_expected = AND(avg_dif < 31, avg_dif > 21)
expected_str = "Expected" if is_expected else "Extreme" if is_extreme else "Unexpected"
expected_str = expected_str & " Difference: " & avg_dif if NOT(is_expected) else expected_str

return "INSUFFICIENT DATA" if NOT(is_data_sufficient) else expected_str
```

This is takes you less than half the time to write up! When you get the spreadsheets turned in from your students and you realize your error, your work isn't lost! Now we can just change the `avg_diff` to use the proportion instead of the raw difference:

```
avg_dif = avg_over_12 / under_12_avg
```

You can also change the threshold values to match this new system. We could say the difference is extreme if the difference is greater than 1.4 or less than 1.10 and the difference is expected if it's between 1.3 and 1.15. This takes you all of 30 seconds to do and ex.py will handle creating the formula for you!

## Usage

ex.py uses a really simple grammar which is described at the top of  [ex.py](ex.py). This grammar should help you linearly construct complex formulas one step at a time. This lets you design the formulas naturally instead of needing to continually wrapping your starting command in increasingly complex commands.

You can pass ex.py a file using command line args:

```sh
python ex.py example.expy
```

If no command line args are passed, ex.py enters an "interpreter" mode where you can enter commands one line at a time.

### Grammar

A valid ex.py script is just defined as a simple list of statements. Each statement can only take up one line and must end with a new line. There are only 2 kinds of statements in this language. Those are assignment statements and return statements.

#### Assignment

An assignment statement allows you to set the value of a variable. This generally takes the form of:

```python
name = value
```

The value on the right hand side can be any combination of valid formula expressions or any variable that was previously defined. For example:

```python
No input files detected. Enter code manually:
> cell = A1 
> cell = 5 + cell
> return cell
=5+A1
```

This snippet will assign the value `A1` to the variable `cell`. The variable is then updated to the value of `5 + cell`. Since `cell` was previously `A1` it is now `5 + A1`.

#### Return

A return statement will evaluate whatever expression it was given and print it to the terminal in the form on a Google Sheets formula. A return statement doesn't have to include the word return. For example:

```python
No input files detected. Enter code manually:
> cells = A1:A1000
> cells
=A1:A1000

> return cells
=A1:A1000
```

Here you can see that entering `cells` is not any different than entering `return cells`. The return keyword is just added for clarity so you can easily identify the outputs. You can also have multiple return statements in one script. You could for example create a script called `test.expy`:

```python
cell1 = A1
cell2 = B1
return cell1 + cell2
return cell1 - cell2
return "EQUAL" if cell1 = cell2 else "NOT EQUAL"
```

Running this file through ex.py would give you:

```
Found return on line 3: "return cell1 + cell2." Result is:
=A1+B1

Found return on line 4: "return cell1 - cell2." Result is:
=A1-B1

Found return on line 5: "return "EQUAL" if cell1 = cell2 else "NOT EQUAL"." Result is:
=IF(A1=B1,"EQUAL","NOT EQUAL")
```

#### Delete

A delete statement will clear the variable entered from the symbol table. Delete can only be called on a valid symbol and will not work on constants. Here is an example:

```python
No input files detected. Enter code manually:
> A = 5
> return A
=5

> del A
Deleted variable A.
> return A
WARNING: Received symbol A, but it doesn't seem to be defined.
=A
```

#### Quit

A quit statement will just exit the program allowing you to resume using your terminal. Here is an example:

```python
No input files detected. Enter code manually:
> quit
Exiting ex.py... Goodbye!
```

#### Expressions

Most normal Google Sheets expressions are supported. This includes arithmetic operators `+, -, *, /`, logical operators `<, >, <=, >=, <>, =`, constants `A1, A1:A10, $A$1, Sheet1!A1, Sheet1!A1:A10, 'Sheet With Spaces'!A1:A10, 1, 3.14, "Strings", TRUE, FALSE`, the string concatenation operator `&`, and functions `INDEX(), AVERAGE(), SUM(), etc`. These can be chained to form arbitrarily complex expressions.

On top of standard `IF(condition, true_value, false_value)`, you can also use ternary expressions. I find the standard ordering of spreadsheet if statements to be really hard to follow. This only gets worse the more complex your branching is. I much prefer to write:

```
true_value if condition else false_value
```

You can chain these together of course to do something like:

```
"Super Cool" if name = "Zach" else "Pretty Cool" if name = "Scott" else "Not Cool"
```

## License

Distributed under the GNU Affero General Public License. See `LICENSE.md` for more information.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/zachoooo/ex.py.svg?style=flat-square
[contributors-url]: https://github.com/zachoooo/ex.py/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/zachoooo/ex.py.svg?style=flat-square
[forks-url]: https://github.com/zachoooo/ex.py/network/members
[stars-shield]: https://img.shields.io/github/stars/zachoooo/ex.py.svg?style=flat-square
[stars-url]: https://github.com/zachoooo/ex.py/stargazers
[issues-shield]: https://img.shields.io/github/issues/zachoooo/ex.py.svg?style=flat-square
[issues-url]: https://github.com/zachoooo/ex.py/issues
[license-shield]: https://img.shields.io/github/license/zachoooo/ex.py.svg?style=flat-square
[license-url]: https://github.com/zachoooo/ex.py/blob/master/LICENSE.md
