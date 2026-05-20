We are going to do a refactor of the codebase, following the SOLID principles. I have a smaller version of these stored in ./cursor/rules/solid-rust.mdc

We should also follow DRY (Don't Repeat Yourself)

## Single Responsibility Principle

The Single Responsibility Principle says that a module, struct, or function should have one clear responsibility and one main reason to change. In Rust, this usually means keeping types focused on what they represent and moving unrelated behavior into separate functions, traits, or modules.

### The Bad Example

Here is a struct that is responsible both for representing data and for handling file input/output:

```rust
use std::fs::File;
use std::io::{self, Read, Write};

struct Config {
    filename: String,
    data: String,
}

impl Config {
    fn new(filename: String, data: String) -> Self {
        Config { filename, data }
    }

    fn read(&mut self) -> io::Result<()> {
        let mut file = File::open(&self.filename)?;
        file.read_to_string(&mut self.data)?;
        Ok(())
    }

    fn write(&self) -> io::Result<()> {
        let mut file = File::create(&self.filename)?;
        file.write_all(self.data.as_bytes())?;
        Ok(())
    }
}
```

In this example, the `Config` struct is responsible for both storing configuration data and performing file I/O. That means changes to either the configuration format or the way files are read and written would require modifying `Config`. This violates SRP because it combines data representation with persistence concerns.

### The Good Example

We refactor the code by separating concerns:

```rust
use std::io::{Read, Write};
use std::fs::File;

        use std::io::Write;

struct Config {
    data: String,
}

impl Config {
    fn new(data: String) -> Self {
        Config { data }
    }
}

struct FileHandler;

impl FileHandler {
    fn read(filename: &str) -> io::Result<Config> {
        let mut file = File::open(filename)?;
        let mut data = String::new();
        file.read_to_string(&mut data)?;
        Ok(Config::new(data))
    }

    fn write(filename: &str, config: &Config) -> io::Result<()> {
        let mut file = File::create(filename)?;
        file.write_all(config.data.as_bytes())?;
        Ok(())
    }
}
```

## Open/Closed Principle

The Open/Closed Principle (OCP) states that software entities should be open for extension but closed for modification.
In Rust, we achieve this through traits and implementations, allowing us to add new behavior without altering existing code.

### The Bad Example

Let's consider this example about a function that calculates areas for different shapes:

```rust
enum Shape {
    Circle(f64),         // radius
    Rectangle(f64, f64), // width, height
}

fn calculate_area(shape: &Shape) -> f64 {
    match shape {
        Shape::Circle(radius) => std::f64::consts::PI * radius * radius,
        Shape::Rectangle(width, height) => width * height,
    }
}
```

In this setup, adding a new shape, like a Triangle, requires modifying the `Shape` enum and the `calculate_area` function. This violates OCP since we have to modify existing code to extend functionality.

### The Good Example

Let's use traits to make the code open for extension:

```rust
trait Shape {
    fn area(&self) -> f64;
}

struct Circle {
    radius: f64,
}

impl Shape for Circle {
    fn area(&self) -> f64 {
        std::f64::consts::PI * self.radius * self.radius
    }
}

struct Rectangle {
    width: f64,
    height: f64,
}

impl Shape for Rectangle {
    fn area(&self) -> f64 {
        self.width * self.height
    }
}

// Adding a new shape doesn't modify existing code
struct Triangle {
    base: f64,
    height: f64,
}

impl Shape for Triangle {
    fn area(&self) -> f64 {
        0.5 * self.base * self.height
    }
}

fn calculate_area(shape: &dyn Shape) -> f64 {
    shape.area()
}
```

In the refactored code, the Shape trait defines a common interface that should be implemented by each shape struct. Adding a new shape involves creating a new struct and impl block without modifying existing code, not even the calculate_area function since it operates on any object that implements Shape.

By adhering to OCP, we ensure our codebase is resilient to change and easy to extend.

## Liskov Substitution Principle

The Liskov Substitution Principle (LSP) asserts that subtypes must be substitutable for their base types without altering the correctness of the program. In Rust, this means that any type implementing a trait should be usable wherever that trait is expected, without causing unexpected behavior or errors.

### The Bad Example

Consider the following example where we define a Bird trait:

```rust
trait Bird {
    fn fly(&self);
}

struct Eagle;

impl Bird for Eagle {
    fn fly(&self) {
        println!("The eagle soars high into the sky.");
    }
}

struct Penguin;

impl Bird for Penguin {
    fn fly(&self) {
        panic!("Penguins can't fly!");
    }
}
```

In this code, both Eagle and Penguin implement the Bird trait, which requires a fly method. While an Eagle can fly, a Penguin cannot. The Penguin's fly method panics when called. Substituting a Penguin where a Bird is expected could lead to a runtime panic, violating the LSP. The fly method's contract implies that any Bird can fly, but Penguin does not fulfill this contract.

### The Good Example

Let's refactor the code to adhere to the LSP by separating flying behavior from the Bird trait:

```rust
trait Bird {
    fn lay_egg(&self);
}

trait Flyable {
    fn fly(&self);
}

struct Eagle;

impl Bird for Eagle {
    fn lay_egg(&self) {
        println!("The eagle lays an egg.");
    }
}

impl Flyable for Eagle {
    fn fly(&self) {
        println!("The eagle soars high into the sky.");
    }
}

struct Penguin;

impl Bird for Penguin { // Note: Penguin does not implement Flyable
    fn lay_egg(&self) {
        println!("The penguin lays an egg.");
    }
}
```

In the refactored code, we've split the behaviors into two traits: Bird and Flyable. The Bird trait includes behaviors common to all birds, such as lay_egg, while the Flyable trait defines the flying behavior. Eagle implements both Bird and Flyable because it can lay eggs and fly. Penguin implements only Bird since it lays eggs but cannot fly.

By doing this, we ensure that any type implementing Flyable truly supports flying, preventing runtime panics. This adheres to the LSP because substituting any Bird or Flyable with their respective implementors will not lead to unexpected behavior.

## Interface Segregation Principle

The Interface Segregation Principle (ISP) advises that clients should not be forced to depend upon interfaces they do not use. In Rust, this means designing small, focused traits.

### The Bad Example

Here's a trait that combines multiple unrelated functionalities:

```rust
trait Entity {
    fn save(&self);
    fn load(&self);
    fn validate(&self) -> bool;
}

struct User;

impl Entity for User {
    fn save(&self) {
        println!("Saving user");
    }

    fn load(&self) {
        println!("Loading user");
    }

    fn validate(&self) -> bool {
        // User validation logic
        true
    }
}

struct Config;

impl Entity for Config {
    fn save(&self) {
        println!("Saving config");
    }

    fn load(&self) {
        println!("Loading config");
    }

    fn validate(&self) -> bool {
        // Config doesn't need validation, but forced to implement
        true
    }
}
```

In this code, Config is forced to implement validate, which may not be relevant. Thus, ISP is violated by requiring structs to implement methods they don't really need.

### The Good Example

Let's split the trait into smaller, more focused traits:

```rust
trait Persistable {
    fn save(&self);
    fn load(&self);
}

trait Validatable {
    fn validate(&self) -> bool;
}

struct User;

impl Persistable for User {
    fn save(&self) {
        println!("Saving user");
    }

    fn load(&self) {
        println!("Loading user");
    }
}

impl Validatable for User {
    fn validate(&self) -> bool {
        // User validation logic
        true
    }
}

struct Config;

impl Persistable for Config {
    fn save(&self) {
        println!("Saving config");
    }

    fn load(&self) {
        println!("Loading config");
    }
}

// No need to implement `Validatable` for `Config`
```

In this code, we have more focused interfaces, that is, smaller traits representing specific behaviors. This means that types can implement only the traits relevant to them, making it easier to compose behaviors without unnecessary code.

By adhering to ISP, we create a modular and flexible codebase where components are not burdened by unnecessary dependencies.

## Dependency Inversion Principle

The Dependency Inversion Principle (DIP) states that high-level modules should not depend on low-level modules; both should depend on abstractions. In Rust, we use traits to define abstractions that decouple modules. Overall, I don't really care too much about this one in Rust. So, you should still see if there are opportunities to do this, but we don't need to do too much with it.

### The Bad Example

Consider a NotificationService that directly depends on a concrete EmailSender:

```rust
struct EmailSender;

impl EmailSender {
    fn send(&self, to: &str, body: &str) {
        println!("Sending email to {}: {}", to, body);
    }
}

struct NotificationService {
    email_sender: EmailSender,
}

impl NotificationService {
    fn new(email_sender: EmailSender) -> Self {
        NotificationService { email_sender }
    }

    fn notify(&self, user: &str, message: &str) {
        self.email_sender.send(user, message);
    }
}
```

In this code, NotificationService depends directly on EmailSender, which is a concrete implementation. This makes it difficult to substitute EmailSender with another sender (e.g., SmsSender), thus violating the DIP by coupling high-level logic with low-level implementation.

### The Good Example

Let's introduce an abstraction using a trait:

```rust
trait Messenger {
    fn send(&self, to: &str, body: &str);
}

struct EmailSender;

impl Messenger for EmailSender {
    fn send(&self, to: &str, body: &str) {
        println!("Sending email to {}: {}", to, body);
    }
}

struct SmsSender;

impl Messenger for SmsSender {
    fn send(&self, to: &str, body: &str) {
        println!("Sending SMS to {}: {}", to, body);
    }
}

struct NotificationService<'a> {
    messenger: &'a dyn Messenger,
}

impl<'a> NotificationService<'a> {
    fn new(messenger: &'a dyn Messenger) -> Self {
        NotificationService { messenger }
    }

    fn notify(&self, user: &str, message: &str) {
        self.messenger.send(user, message);
    }
}
```

In the refactored code, Messenger trait defines an abstraction for sending messages. NotificationService depends on the Messenger trait, not on a concrete implementation; hence, we can inject any messenger that implements Messenger, promoting flexibility.

By adhering to DIP, we create a modular architecture where components are interchangeable and extensible.

## Don't repeat yourself

Traits and Generics: Define shared behavior across different types using traits. Generics allow functions to operate on any type that implements specific trait bounds, reducing the need for duplicate function implementations.

Macros (macro_rules! and Procedural): Factor out repetitive boilerplate that cannot be handled by standard functions, such as repeating complex test suites or implementing the same logic for multiple primitive types.

Closures: Use closures to capture local environments and abstract away repetitive execution patterns within a single scope.

Enums and Pattern Matching: Use enums to represent varying states or data types, then use pattern matching to handle them in a single, unified logic path rather than separate functions.

Ownership and References: Design functions to take references (&T) instead of taking ownership (T) where possible. This allows the same logic to be reused across different parts of a program without unnecessary data cloning.
