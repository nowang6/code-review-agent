https://100go.co/#ignoring-that-elements-are-copied-in-range-loops-30

## 1 Naming Conventions

### 1.1 Use CamelCase or camelCase

The convention in Go is to use MixedCaps or mixedCaps rather than underscores to write multiword names.

Further more, abbreviations are always written with the same case, which means `HTTPPort`, not `HttpPort`.

### 1.2 Don't Use `ALL_CAPS`

When it's not an environment variable, do not use `ALL_CAPS` because it looks like one.

### 1.3 Short Names Can Be Used in Context

Avoid long names with redundant information which can be inferred from the context.

Example:

- Avoid: `basicAuthUsername, basicAuthPassword, _ := r.BasicAuth()`
- Prefer: `username, password, _ := r.BasicAuth()`

Because in the context, it can be inferred the username and password are for basic auth.

### 1.4 Be Consistent with Function Calls

If `func foo()` returns a `code`, then `returnCode := foo()` is more accurate than `returnVal := foo()` - the result variable naming should be consistent with the function called.

---

## 2 Adding Code in Existing Functions and Structs

Think stratigically about _where to add the new code._ Study existing code and try to discover a logic or pattern.

Order:

- A special order: For example, if you have a validation function that validates user inputs against a couple of rules and the code uses if/switch and puts them in an alphabetical order, when adding new code, you should probably follow that existing pattern.
- Anywhere? This could work in certain cases. For the same example, if existing validation rules are organized in no particular order and now you are adding a new rule, it's probably ok to add it anywhere in the validation function. At the beginning, at the end, or even in the middle.
- Some logical order: For the same example, if the new rule you add is a naming convention (e.g., it must start with a certain prefix, it must follow a regex, etc.), then there is a correct place to add it and it's the very beginning, because it makes more sense: if the name doesn't even follow the convention, there is no need to check for other rules. Lazy thinking would just add this new rule anywhere or just at the bottom of the function because it's just another rule to be added to a validation function and it's the easiest to do; stratigic thinking would try to discover the logic and find a best place.

Ownership:

- When adding a new field/flag to an existing struct, think about if the field really _belongs_ to the thing where you are adding it to. Do you add it there just because it's simple to do so, or does it truly belong to it? If not, should a new struct be created specifically for it? Understanding existing code before working on it.

An example on order:

Avoid:

```go
MkdirOptions{
	MakeParents: true,
	ExistOK:     true,
	Chown:       true,
	Chmod:       true,
	UserID:      sys.UserID(*uid),
	GroupID:     sys.GroupID(*gid),
}
```

Prefer:

```go
MkdirOptions{
	MakeParents: true,
	ExistOK:     true,
	Chmod:       true,
	Chown:       true,
	UserID:      sys.UserID(*uid),
	GroupID:     sys.GroupID(*gid),
}
=
```

(Pay attention to the place of `Chown` because it relates more to `UserID` and `GroupID`.)

---

## 3 Refactor

Compare the logic before/after, there should be no behaviour change, because it's a "refactor". Make sure they are 100% the same.

---

## 4 Code Style

### 4.1 Functions

#### 4.1.1 Function Parameters

Use Go style:

- Avoid `func foo(a string, b string, c string)`
- Prefer `func foo(a, b, c string)`

#### 4.1.2 Named Arguments

Clearer to have named arguments when you're returning multiple things of the same type, and it's not clear which is which. Example:

- Avoid: `func foo() (<-chan servicelog.Entry, <-chan servicelog.Entry) {}`
- Prefer: `func foo() (stdoutCh <-chan servicelog.Entry, stderrCh <-chan servicelog.Entry) {}`

#### 4.1.3 Short Variable Declarations in Functions

Inside a function, use the more go-idiomatic `:=` short assignment for var declaration with implicit type.

- Prefer: `a := 0`
- Avoid: `var a = 0`

#### 4.1.4 Don't Repeat Yourself

Example:

Avoid:

```go
// Create a single directory and perform chmod/chown operations according to options.
func mkdir(path string, perm os.FileMode, options *MkdirOptions) error {
	// multiple options != nil
	if options != nil && options.Chown {
		// ...
	}

	// multiple options != nil
	if options != nil && options.Chmod {
		// ...
	}

	// ...
}
```

Prefer:

```go
func Mkdir(path string, perm os.FileMode, options *MkdirOptions) error {
	// avoid multiple options != nil
	if options == nil {
		options = &MkdirOptions{}
	}
	
	if options.Chown {
		// ...
	}

	if options.Chmod {
		// ...
	}

	// ...
}

```

#### 4.1.5 Avoid Very Small Functions

For example, a one-liner unexported function in the same package probably isn't necessary.

Another example:

```go
func (rb *RingBuffer) Positions() (start RingPos, end RingPos) {
	rb.rwlock.RLock()
	defer rb.rwlock.RUnlock()
	return rb.positions()
}

func (rb *RingBuffer) positions() (start RingPos, end RingPos) {
	return rb.readIndex, rb.writeIndex
}
```

The two functions doesn't provide much value because we can simply use 

```go
rb.rwlock.RLock()
defer rb.rwlock.RUnlock()

start := rb.readIndex
stop := rb.writeIndex
```

Another example: `strings.Contains` instead of creating a function `containsSubstring`.

Exception: If a very short function is used repeatedly in different places and increases readability, maybe we can keep it.

#### 4.1.6 Cuddled Braces

Avoid:

```go
err = osutil.Mkdir(
	filepath.Dir(filename),
	0700,
	&osutil.MkdirOptions{
		ExistOK: true,
		Chmod:   true,
		UserID:  uid,
		GroupID: gid,
	},
)
```

Prefer:

```go
err = osutil.Mkdir(filepath.Dir(filename), 0700, &osutil.MkdirOptions{
	ExistOK: true,
	// ...
})
```

#### 4.1.7 Exported V.S. Unexported

`lowerCaseFunction` if it doesn't need to be exported (for example, helper functions). Think carefully about if it really needs to be exported.

#### 4.1.8 Guard `nil` Values

Guard with `if foo != nil { }` as early as possible, before the first possible access.

#### 4.1.9 Defer

If you are adding a piece of code that could potentially return prematurely in a function where there are deferred calls, you'd probably want to add your new code _after_ the deferred calls to make sure the defer is always called.

### 4.2 Grouping

Grouping related fields together in struct.

For example:

Avoid:

```go
type MkdirOptions struct {
	MakeParents bool

	ExistOK bool

	Chmod bool

	Chown bool

	UserID sys.UserID
	
	GroupID sys.GroupID
}
```

Prefer:

```go
type MkdirOptions struct {
	MakeParents bool

	ExistOK bool

	Chmod bool

	Chown bool
	UserID sys.UserID
	GroupID sys.GroupID
}
```

Because all these three fields are related to ownership.

### 4.3 Synchronization

#### 4.3.1 Locks

If func A calls B, B locks/unlocks a lock, then A also locks/unlocks it, it's messy and inefficient. Maybe only do one lock in A.

Example:

Avoid:

```go
func (rb *RingBuffer) reverseLinePosition(n int) RingPos {
	rb.rwlock.RLock()
	defer rb.rwlock.RUnlock()
	// ...
}

func (rb *RingBuffer) HeadIterator(lines int) Iterator {
	firstLine := rb.reverseLinePosition(lines)
	rb.rwlock.RLock()
	defer rb.rwlock.RUnlock()
	// ...
}
```

Prefer:

```go
func (rb *RingBuffer) reverseLinePosition(n int) RingPos {
	// ...
	// no lock
}

func (rb *RingBuffer) HeadIterator(lines int) Iterator {
	rb.rwlock.RLock()
	defer rb.rwlock.RUnlock()
	firstLine := rb.reverseLinePosition(lines)
	// ...
}
```

#### 4.3.2 Channels

Cancellation channels should be unbuffered channels that are closed.

```go
	stopStdout := make(chan struct{})
	// ...
	close(stopStdout)
```

#### 4.3.3 Channel over Sleep

Prefer:

```go
timeoutCh := time.After(timeout)
for {
    select {
    case foo, ok := <-fooCh: ...
    case <-timeoutCh: ...
	}
}
```

instead of sleep.

#### 4.3.4 Switch Default

For defensive programming, probably best to add a default case.

### 4.4 Strings

#### 4.4.1 String Concatenation V.S. `fmt.Sprintf`

It's simpler and more efficient to avoid fmt.Sprintf for simple concatenation, like `"FOO="+foo` over `fmt.Sprintf("FOO=%s", foo)`.

_Although this is debatable, because from the perspective of readability, one can argue that `fmt.Sprintf` wins. When in doubt, respect existing code convention._

#### 4.4.2 Multiline Strings

It's easier to use `[1:]` for readability. Example:

Avoid:

```go
	expected := `This
is a 
multiline
string.
`
```

Prefer:

```go
	expected := `
This
is a 
multiline
string.
`[1:]
```

However, if it's YAML, YAML doesn't care about an empty line in the beginning, so it's OK to not have `[1:]`:

```go
	someYAML := `
key: value
foo: bar
`
```

### 4.5 Regex

We shouldn't re-compile the regex (a relatively expensive operation) every time we call a function. The regex compliation should be done at the top-level so `MustCompile` is run once on package init.

Avoid:

```go
func foo() {
	var nameRegexp = regexp.MustCompile(`^[a-z0-9]+$`)
	// ...
}

```

Prefer:

```go
var nameRegexp = regexp.MustCompile(`^[a-z0-9]+$`)

func foo(name string) {
	if !nameRegexp.MatchString(name) {
		// ...
	}
	// ...
}
```

### 4.6 Permissions

Prefer `0o755` over `0755` format to make it super-clear it's octal, unless it's already `0755` in existing code.

### 4.7 `iota`

The `iota` identifier is used in const declarations to simplify definitions of incrementing numbers. The `iota` keyword represents successive integer constants 0, 1, 2, ... It resets to 0 whenever the word const appears in the source code, and increments after each const specification. To avoid getting the zero value by accident, we can start a list of constants at 1 instead of 0 from `iota + 1`.

---

## 5 Error Handling

### 5.1 Be Specific

When creating an error messages, think from the user's perspective, and see what specific messages would help them the most.

For example, if the user input layer label is `pebble-test` but pebble-* is reserved:

- `fmt.Sprintf("cannot use reserved layer label %q", layer.Label)`
- ``cannot use reserved label prefix "pebble-"``

Is it because the `pebble-test` label is reserved? Or is it because the `pebble-` prefix is reserved? The latter is true, hence prefer the second error message, avoid the first. Be specific.

For another example:

- Avoid `fmt.Println("Setup failed with error:", err)` (Ambiguous)
- Prefer `fmt.Println("Cannot build pebble binary:", err)` (Specific, f we know why it fails)

### 5.2 Be Consistent

Be consistent in error messages with other code in the same function or even the same module. For example, if existing code uses:

```go
if !osutil.IsDir(o.pebbleDir) {
	return nil, fmt.Errorf("directory %q does not exist", o.pebbleDir)
}
```

When adding a new error for no write permissions:

- Avoid: `fmt.Errorf("no write permission in directory %q", o.pebbleDir)`
- Prefer: `fmt.Errorf("directory %q not writeable, o.pebbleDir)` (Follow existing convention)

### 5.3 Use `errors.Is`

Use `errors.Is()` to check error types.

```go
if errors.Is(err, fs.ErrNotExist) {
	// ...
}
```

### 5.4 Use Custom Error Types

Don't check error string, which is fragile; use custom error type.

Examples:

```go
type detailsError struct {
	error
	details string
}

message := err.Error()

var detailsErr *detailsError

if errors.As(err, &detailsErr) && detailsErr.Details() != "" {
	message += "; " + detailsErr.Details()
}
```

### 5.5 Variables

Avoid hard-coded value in errors. Example:

- Avoid: `fmt.Errorf("stopped before the 1 second okay delay")`
- Prefer: `fmt.Errorf("stopped before the %s okay delay", okayDelay)`

---

## 6 Tests

### 6.1 Test Naming

Put tremendous effort in test names.

Do not just use some casual name that comes to you off the top of the head, but use meaningful, precise naems that follow the convention of existing code.

For the same example as mentioned in the error messages section, if we have a validation function that validates the user input layer label and see if reserved prefixes are used:

- Follow Convention: If all tests in the same file follows the "Test(Do)Something(SomeFeature)", like `TestParseCommand`, `TestMergeServiceContextOverrides`, follow the naming convention when adding a new test. Like `TestPebbleLabelPrefixReserved` probably fits better in the context than `TestCannotUseReservedPrefixInLayers`.
- Be Precise: Are we testing parsing the layer (then see if the label is valid) or are we testing the labels themselves? The latter is more true, hence `TestParseLayer` is not as accurate as `TestLabel`. For another example, don't use `TestNormal` which is too generic, but `TestStartupEnabledServices` is a whole lot better as the name of a test.

Following the rules above, the best name probably is `TestLabelReservedPrefix` or `TestLabelReservedPrefix`.

### 6.2 Variable Names

Use `foo`, `bar`, `baz`, `qux`, `quux`, and other metasyntactic variables and placeholder names in tests.

However, check existing code and be consistent: If existing tests use "alice" and "bob" or meaningful variable names like `pebble-service-name`, follow the convention. Vice versa, do not use very specific names that actually mean something when it's just a generic name.

### 6.3 Copy-Paste

When adding unit tests, it's common to copy-paste an existing test which is similar and modify that because it's quicker. It's OK to copy-paste, but examine the naming, the logic, remove unnecessary things carefully, treat it as if you are writing a new test.

It's also OK to use a few lines of duplicated code if it makes the test more clear instead of creating helper functions, see [Advanced Testing with Go - Mitchell Hashimoto](https://www.youtube.com/watch?v=8hQG7QlcLBk).

### 6.4 Setup/Teardown

It is sometimes necessary for a test to do extra setup or teardown. To support these and other cases, if a test file contains a function:

`func TestMain(m *testing.M)`

Then the generated test will call `TestMain(m)`` instead of running the tests directly.

TestMain runs in the main goroutine and can do whatever setup and teardown is necessary around a call to `m.Run`.

A simple implementation of TestMain is:

```go
func TestMain(m *testing.M) {
	// global setup here
    code := m.Run() 
    // global tear down here
    os.Exit(code)
}
```

TestMain is a low-level primitive and should not be necessary for casual testing needs, where ordinary test functions suffice.

### 6.5 ENV Vars

`Setenv` calls `os.Setenv(key, value)` and uses Cleanup to restore the environment variable to its original value after the test. So, instead of doing:

```go
os.Setenv("FOO", "1")
defer os.Setenv("FOO", "")
```

We can simply: `t.Setenv("FOO", "1")`.

### 6.6 Sending Signals

In the context of process termination, SIGTERM (signal 15) is a polite request for a process to shut down gracefully, allowing it to perform cleanup tasks, while SIGKILL (signal 9) forcefully terminates the process immediately, without any cleanup. In tests, try to use SIGTERM instead of SIGKILL for a graceful termination.

### 6.7 Avoid Cached Results with `-count=1`

Test outputs are cached to speed up tests. If the code doesn't change, the test output shouldn't change either. Of course this is not necessarily true, tests may read info from external sources or may use time and random related data which could change from run to run.

When you request multiple test runs using the `-count` flag, obviously the intention is to run the tests multiple times, there's no logic running them just once and show n-1 times the same result. So `-count` triggers omitting the cached results. Setting `-count=1` explicitly (although the default value is also 1, but the behaviour is different) will simply cause running the tests once, omitting previous cached outputs.

### 6.8 `t.Fatalf` or `t.Errorf`?

Be careful, if test should continue? This makes a difference.

### 6.9 Ports

When testing a port, use something high like above 60000 so that it's not likely to be used, compared to 4000 or 8080.

### 6.10 Comments in Tests

All complex tests should have a verbose comment describing what they are testing.

### 6.11 Philosophies

#### 6.11.1 Avoid Defaults

Try not to have defualts for tests, as they often get in the way of additional tests.

#### 6.11.2 Check Behaviour, Not Logs

Do not bother checking the logs in the tests, because stable log formatting isn't part of the contract. Check the expected behaviour or output.

#### 6.11.3 Time-Dependent Tests

When we need to wait in tests, like a for loop or a sleep, make sure the time is long enough to ensure even when the CPU is loaded, it can still pass, and make sure it's not too long as to slow the tests drastically. Use a reasonable value, refer to existing tests, follow existing convention, and maybe run the test multiple times to get a reasonable value - do not simply set a value and that's it.

#### 6.11.4 Test Coverage

Do the tests cover all scenarios?

---

## 7 Comments

### 7.1 Be Precise

Choice of word, especially verbs. Return an error? Thrown an error? etc.

### 7.2 Helper/Utility Functions

Add commments for complex helper/utility functions to describe their use.

### 7.3 Don't Write Obvious Comments

Either leave obvious comment off, or make it more useful.

For example:

- Avoid: "MkdirOptions is a struct of options used for Mkdir()."
- Prefer: Either remove the comment, or: "MkdirOptions holds the options for a call to Mkdir."

For another example:

```go
// if path already exists
if s, err := os.Stat(path); err == nil {
	// ...
}
```

The comment probably isn't necessary since the following line is straightforward and easy to understand.

### 7.4 Use TODO

Add a "TODO" in the comment when handling temporary workarounds so it's easier to grep for later.

### 7.5 House keeping rule

Be careful when the code you change has some comments/notes or even links to issues. Read them carefully. If your code change solves the issue and it no longer holds true, remove it - keep the comment clean and true.

### 7.6 Spell-Check and Grammar-Check Comments

Do this.

### 7.7 Review Newly Added/Updated Comments Before Commiting

Are they precise, are the specific, are they correct, both gramatically and literally.
