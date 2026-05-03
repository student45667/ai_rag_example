# C++ Programming - Comprehensive Guide for Engineers and Developers

## Who This Guide Is For

This guide targets:
- **C developers** transitioning to C++
- **Embedded systems engineers** using modern C++ (C++11/14/17)
- **Firmware developers** building hardware abstraction layers
- **Systems programmers** building drivers, tools, and frameworks

**Assumed knowledge:** C programming fundamentals (see C Programming Guide)

---

## Table of Contents

1. [C++ vs C - Key Differences](#1-c-vs-c---key-differences)
2. [Setup and Compilation](#2-setup-and-compilation)
3. [C++ Basics](#3-c-basics)
4. [References and const](#4-references-and-const)
5. [Functions in C++](#5-functions-in-c)
6. [Classes and Objects](#6-classes-and-objects)
7. [Constructors and Destructors](#7-constructors-and-destructors)
8. [Inheritance](#8-inheritance)
9. [Polymorphism and Virtual Functions](#9-polymorphism-and-virtual-functions)
10. [Operator Overloading](#10-operator-overloading)
11. [Templates](#11-templates)
12. [Standard Template Library (STL)](#12-standard-template-library-stl)
13. [Exception Handling](#13-exception-handling)
14. [Smart Pointers](#14-smart-pointers)
15. [Modern C++ Features (C++11/14/17)](#15-modern-c-features-c111417)
16. [Embedded C++ Patterns](#16-embedded-c-patterns)
17. [Best Practices](#17-best-practices)

---

## 1. C++ vs C - Key Differences

```cpp
/* key_differences.cpp - What's new in C++ */

// C++ ADDS to C:
// 1. Classes and Objects (OOP)
// 2. References
// 3. Function overloading
// 4. Default parameters
// 5. Templates (generic programming)
// 6. Namespaces
// 7. Exception handling
// 8. RAII (Resource Acquisition Is Initialization)
// 9. Standard Template Library (STL)
// 10. Smart pointers
// 11. Lambda expressions (C++11)
// 12. Move semantics (C++11)

// WHAT STAYS THE SAME:
// - All C syntax works in C++
// - Pointers, arrays, structs
// - Bit manipulation
// - Memory model
// - Preprocessor

// C vs C++ for embedded:
// C:   Manual everything, predictable, minimal overhead
// C++: Zero-cost abstractions, RAII, type safety, harder to misuse
```

### Philosophy Comparison

```
C Philosophy:
  Trust the programmer
  Minimal runtime
  You get what you pay for

C++ Philosophy:
  Don't pay for what you don't use
  Zero-overhead abstractions
  Type safety without runtime cost
  Make interfaces easy to use correctly, hard to use wrong
```

---

## 2. Setup and Compilation

### Install G++ Compiler

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential g++ gdb

# Verify
g++ --version
# g++ (Ubuntu 11.3.0) 11.3.0

# Additional tools
sudo apt install valgrind cppcheck clang-format
```

### Compilation

```bash
# Basic compilation
g++ main.cpp -o program

# Recommended development flags
g++ -Wall -Wextra -std=c++17 -g main.cpp -o program

# Release build
g++ -O2 -std=c++17 -DNDEBUG main.cpp -o program

# Multiple files
g++ -Wall -std=c++17 main.cpp sensor.cpp uart.cpp -o program

# With libraries
g++ -Wall -std=c++17 main.cpp -o program -lpthread -lm

# Generate assembly (useful for embedded)
g++ -S -O2 -std=c++17 main.cpp -o main.s

# C++ standards:
# c++11  - Lambdas, auto, nullptr, smart pointers, move semantics
# c++14  - Generic lambdas, make_unique
# c++17  - Structured bindings, if constexpr, std::optional
# c++20  - Concepts, ranges, coroutines (latest major)
```

---

## 3. C++ Basics

### New vs C

```cpp
/* basics.cpp - C++ fundamentals */

#include <iostream>    // C++ I/O (replaces stdio.h)
#include <string>      // C++ string class
#include <cstdint>     // Same as stdint.h
#include <cstring>     // Same as string.h

// NAMESPACES (organize code, avoid name conflicts)
namespace SensorLib {
    const float MAX_VOLTAGE = 3.3f;
    
    void initialize(void) {
        std::cout << "SensorLib initialized\n";
    }
}

namespace DriverLib {
    const float MAX_VOLTAGE = 5.0f;  // Different MAX_VOLTAGE!
    
    void initialize(void) {
        std::cout << "DriverLib initialized\n";
    }
}

int main() {
    // C++ OUTPUT (no format strings needed!)
    std::cout << "Hello, Engineer!" << std::endl;
    std::cout << "Value: " << 42 << " Float: " << 3.14 << "\n";
    
    // C++ INPUT
    int value;
    std::cout << "Enter value: ";
    std::cin >> value;
    std::cout << "You entered: " << value << "\n";
    
    // 'using' to avoid std:: prefix
    using std::cout;
    using std::endl;
    cout << "Without std::" << endl;
    
    // Namespace usage
    SensorLib::initialize();
    DriverLib::initialize();
    
    // Access namespace members
    cout << "Sensor max voltage: " << SensorLib::MAX_VOLTAGE << "\n";
    cout << "Driver max voltage: " << DriverLib::MAX_VOLTAGE << "\n";
    
    // C++ STRING (much better than char arrays!)
    std::string name = "ADXL362";
    name += " Sensor";           // Concatenation
    cout << "Name: " << name << "\n";
    cout << "Length: " << name.length() << "\n";
    cout << "Find 'Sensor': " << name.find("Sensor") << "\n";
    
    // String to number (C++11)
    std::string num_str = "12345";
    int num = std::stoi(num_str);          // String to int
    float flt = std::stof("3.14");         // String to float
    std::string back = std::to_string(42); // Number to string
    
    cout << "num: " << num << ", flt: " << flt << ", back: " << back << "\n";
    
    // AUTO (type inference - let compiler figure it out)
    auto x = 42;          // int
    auto y = 3.14;        // double
    auto z = 3.14f;       // float
    auto s = std::string("hello");  // std::string
    
    cout << "auto types: " << x << " " << y << " " << z << "\n";
    
    // NULLPTR (replaces NULL - type safe!)
    int *ptr = nullptr;   // Better than NULL or 0
    if (ptr == nullptr) {
        cout << "Pointer is null\n";
    }
    
    // RANGE-BASED FOR LOOP (C++11)
    int arr[] = {1, 2, 3, 4, 5};
    for (int val : arr) {
        cout << val << " ";
    }
    cout << "\n";
    
    // With auto
    for (auto val : arr) {
        cout << val * 2 << " ";
    }
    cout << "\n";
    
    return 0;
}
```

---

## 4. References and const

```cpp
/* references.cpp - C++ references (key C++ feature!) */

#include <iostream>
#include <cstdint>

// REFERENCE: alias for another variable
// Like a pointer but:
//   - Cannot be null
//   - Cannot be reseated (always refers to same object)
//   - No need to dereference

// ================================================================
// PASS BY VALUE (copy - expensive for large objects!)
// ================================================================
int double_val_copy(int x) {
    x *= 2;      // Modifies copy, not original
    return x;
}

// ================================================================
// PASS BY POINTER (C style)
// ================================================================
void double_val_ptr(int *x) {
    if (x != nullptr) *x *= 2;   // Must check for null!
}

// ================================================================
// PASS BY REFERENCE (C++ style - preferred!)
// ================================================================
void double_val_ref(int &x) {
    x *= 2;      // Modifies original (no * needed)
    // x cannot be null - guaranteed valid!
}

// ================================================================
// CONST REFERENCE (read-only access, no copy!)
// Best for passing large objects!
// ================================================================
void print_data(const std::string &data) {
    // Cannot modify data - protected by const
    // No copy made - efficient
    std::cout << "Data: " << data << "\n";
}

// ================================================================
// RETURN BY REFERENCE (careful with lifetime!)
// ================================================================
int& get_max(int &a, int &b) {
    return (a > b) ? a : b;  // Returns reference to existing variable
}

// ================================================================
// PRACTICAL: Swap without pointers
// ================================================================
void swap(int &a, int &b) {
    int temp = a;
    a = b;
    b = temp;
}

// ================================================================
// SENSOR CONFIG EXAMPLE (pass by reference pattern)
// ================================================================
struct SensorConfig {
    uint16_t sample_rate;
    uint8_t  resolution;
    float    scale_factor;
    bool     enabled;
};

void configure_defaults(SensorConfig &config) {
    config.sample_rate  = 100;    // Hz
    config.resolution   = 12;     // bits
    config.scale_factor = 1.0f;
    config.enabled      = true;
}

void print_config(const SensorConfig &config) {
    std::cout << "Sample rate: " << config.sample_rate << " Hz\n";
    std::cout << "Resolution: " << (int)config.resolution << " bits\n";
    std::cout << "Scale: " << config.scale_factor << "\n";
    std::cout << "Enabled: " << (config.enabled ? "yes" : "no") << "\n";
}

int main() {
    // References
    int a = 10;
    int &ref = a;    // ref is an alias for a
    
    std::cout << "a: " << a << ", ref: " << ref << "\n";  // Both 10
    ref = 20;        // Changes a through reference
    std::cout << "a after ref=20: " << a << "\n";         // 20
    
    // Pass by different methods
    int val = 5;
    std::cout << "\nPass by value:     " << double_val_copy(val) << ", val=" << val << "\n";
    
    double_val_ptr(&val);
    std::cout << "Pass by pointer:   val=" << val << "\n";  // val changed
    
    double_val_ref(val);
    std::cout << "Pass by reference: val=" << val << "\n";  // val changed
    
    // Const reference
    std::string large_data = "Large string that we don't want to copy!";
    print_data(large_data);  // No copy made!
    
    // Return reference
    int x = 10, y = 20;
    get_max(x, y) = 100;    // Assign to returned reference!
    std::cout << "x=" << x << ", y=" << y << "\n";  // y=100
    
    // Swap
    swap(x, y);
    std::cout << "After swap: x=" << x << ", y=" << y << "\n";
    
    // Sensor config
    SensorConfig config;
    configure_defaults(config);
    print_config(config);
    
    return 0;
}
```

---

## 5. Functions in C++

```cpp
/* functions_cpp.cpp - Enhanced functions in C++ */

#include <iostream>
#include <cstdint>
#include <cmath>

// ================================================================
// FUNCTION OVERLOADING
// Same name, different parameters!
// ================================================================
void print(int x)         { std::cout << "int: " << x << "\n"; }
void print(float x)       { std::cout << "float: " << x << "\n"; }
void print(const char *s) { std::cout << "string: " << s << "\n"; }
void print(bool b)        { std::cout << "bool: " << (b ? "true" : "false") << "\n"; }

// Overloaded sensor read functions
float read_sensor(uint8_t channel)              { return channel * 3.3f / 255; }
float read_sensor(uint8_t channel, uint8_t avg) { 
    float sum = 0;
    for (uint8_t i = 0; i < avg; i++) sum += channel * 3.3f / 255;
    return sum / avg;
}

// ================================================================
// DEFAULT PARAMETERS
// ================================================================
void configure_uart(
    uint32_t baud    = 115200,    // Default baud rate
    uint8_t  data    = 8,         // Default data bits
    uint8_t  stop    = 1,         // Default stop bits
    char     parity  = 'N'        // Default no parity
) {
    std::cout << "UART: " << baud << " " << (int)data << (int)stop << parity << "\n";
}

// ================================================================
// INLINE FUNCTIONS (hint to compiler to expand inline)
// Better than macros - type safe!
// ================================================================
inline float celsius_to_fahrenheit(float c) {
    return c * 9.0f / 5.0f + 32.0f;
}

inline uint8_t clamp_byte(int val) {
    return (val < 0) ? 0 : (val > 255) ? 255 : (uint8_t)val;
}

// ================================================================
// CONSTEXPR FUNCTIONS (compile-time evaluation!)
// Computed at compile time, not runtime!
// Great for embedded: puts values in flash, not RAM!
// ================================================================
constexpr uint32_t calculate_prescaler(uint32_t sys_clock, uint32_t target_freq) {
    return sys_clock / target_freq - 1;
}

constexpr float bytes_to_mb(uint32_t bytes) {
    return bytes / (1024.0f * 1024.0f);
}

// Usage at compile time:
constexpr uint32_t SYS_CLOCK = 168000000;  // 168 MHz STM32
constexpr uint32_t TARGET_FREQ = 1000;      // 1 kHz timer
constexpr uint32_t PRESCALER = calculate_prescaler(SYS_CLOCK, TARGET_FREQ);
// PRESCALER is computed at compile time!

// ================================================================
// LAMBDA EXPRESSIONS (C++11 - anonymous functions)
// ================================================================
int main() {
    // Overloading
    print(42);
    print(3.14f);
    print("hello");
    print(true);
    
    // Default parameters
    configure_uart();                     // All defaults
    configure_uart(9600);                 // 9600 baud, rest default
    configure_uart(9600, 8, 2, 'E');     // All specified
    
    // Inline functions
    std::cout << celsius_to_fahrenheit(100.0f) << "°F\n";  // 212.0
    std::cout << (int)clamp_byte(300) << "\n";              // 255
    
    // constexpr
    std::cout << "Prescaler: " << PRESCALER << "\n";  // Computed at compile time!
    
    // Lambda - basic
    auto add = [](int a, int b) { return a + b; };
    std::cout << "add(3, 4) = " << add(3, 4) << "\n";
    
    // Lambda - capture variables
    float scale = 2.5f;
    auto scale_val = [scale](float x) { return x * scale; };
    std::cout << "scale(10) = " << scale_val(10.0f) << "\n";
    
    // Lambda - capture by reference
    int count = 0;
    auto increment = [&count]() { count++; };
    increment(); increment(); increment();
    std::cout << "count: " << count << "\n";  // 3
    
    // Lambda as callback (practical use)
    int arr[] = {5, 2, 8, 1, 9, 3};
    uint8_t n = sizeof(arr) / sizeof(arr[0]);
    
    // Sort with custom comparator (lambda!)
    auto compare = [](int a, int b) { return a < b; };
    // Bubble sort with lambda comparator
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (!compare(arr[j], arr[j+1])) {
                std::swap(arr[j], arr[j+1]);
            }
        }
    }
    
    for (int i = 0; i < n; i++) std::cout << arr[i] << " ";
    std::cout << "\n";
    
    return 0;
}
```

---

## 6. Classes and Objects

```cpp
/* classes.cpp - Object-Oriented Programming in C++ */

#include <iostream>
#include <cstdint>
#include <string>
#include <cstring>

// ================================================================
// BASIC CLASS (Hardware sensor abstraction)
// ================================================================
class Sensor {
public:    // Accessible from anywhere
    static uint8_t sensor_count;  // Shared across ALL instances
    
private:   // Only accessible within this class
    uint8_t  id_;
    std::string name_;
    float    value_;
    bool     enabled_;
    uint16_t sample_rate_;

protected: // Accessible in this class and derived classes
    float    calibration_offset_;

public:
    // ── GETTERS (const: doesn't modify object) ──────────────────
    uint8_t     get_id()          const { return id_; }
    std::string get_name()        const { return name_; }
    float       get_value()       const { return value_; }
    bool        is_enabled()      const { return enabled_; }
    uint16_t    get_sample_rate() const { return sample_rate_; }
    
    // ── SETTERS ─────────────────────────────────────────────────
    void set_sample_rate(uint16_t rate) {
        if (rate > 0 && rate <= 1000) {  // Validate input
            sample_rate_ = rate;
        }
    }
    
    void enable()  { enabled_ = true;  }
    void disable() { enabled_ = false; }
    
    // ── CONSTRUCTOR ──────────────────────────────────────────────
    Sensor(uint8_t id, const std::string &name, uint16_t sample_rate = 100)
        : id_(id),                      // Member initializer list (preferred!)
          name_(name),                  // More efficient than assignment
          value_(0.0f),
          enabled_(false),
          sample_rate_(sample_rate),
          calibration_offset_(0.0f)
    {
        sensor_count++;  // Track total sensors
        std::cout << "Sensor created: " << name_ << " (ID=" << (int)id_ << ")\n";
    }
    
    // ── DESTRUCTOR ───────────────────────────────────────────────
    ~Sensor() {
        sensor_count--;
        std::cout << "Sensor destroyed: " << name_ << "\n";
    }
    
    // ── METHODS ─────────────────────────────────────────────────
    virtual float read() {
        // Simulate reading (would access hardware in real code)
        value_ = calibration_offset_ + id_ * 1.5f;
        return value_;
    }
    
    void print_info() const {
        std::cout << "Sensor " << (int)id_ << " (" << name_ << "):\n";
        std::cout << "  Value: " << value_ << "\n";
        std::cout << "  Rate:  " << sample_rate_ << " Hz\n";
        std::cout << "  State: " << (enabled_ ? "enabled" : "disabled") << "\n";
    }
    
    void calibrate(float offset) {
        calibration_offset_ = offset;
        std::cout << "Calibrated with offset: " << offset << "\n";
    }
};

// Initialize static member outside class
uint8_t Sensor::sensor_count = 0;

// ================================================================
// PRACTICAL CLASS: UART Driver
// ================================================================
class UART {
private:
    uint32_t    baud_rate_;
    uint8_t     data_bits_;
    uint8_t     stop_bits_;
    char        parity_;
    bool        initialized_;
    
    // Circular buffer
    static const uint8_t BUF_SIZE = 64;
    uint8_t     rx_buf_[BUF_SIZE];
    uint8_t     rx_head_;
    uint8_t     rx_tail_;
    uint8_t     rx_count_;
    
public:
    UART(uint32_t baud = 115200)
        : baud_rate_(baud),
          data_bits_(8),
          stop_bits_(1),
          parity_('N'),
          initialized_(false),
          rx_head_(0),
          rx_tail_(0),
          rx_count_(0)
    {
        memset(rx_buf_, 0, sizeof(rx_buf_));
    }
    
    bool init() {
        // Hardware initialization would go here
        initialized_ = true;
        std::cout << "UART initialized: " << baud_rate_ << " baud\n";
        return true;
    }
    
    bool send(const uint8_t *data, uint16_t len) {
        if (!initialized_) return false;
        // Simulate send
        std::cout << "UART TX: " << len << " bytes\n";
        return true;
    }
    
    bool push_rx(uint8_t byte) {
        if (rx_count_ >= BUF_SIZE) return false;  // Buffer full
        rx_buf_[rx_head_] = byte;
        rx_head_ = (rx_head_ + 1) % BUF_SIZE;
        rx_count_++;
        return true;
    }
    
    bool pop_rx(uint8_t &byte) {
        if (rx_count_ == 0) return false;  // Buffer empty
        byte = rx_buf_[rx_tail_];
        rx_tail_ = (rx_tail_ + 1) % BUF_SIZE;
        rx_count_--;
        return true;
    }
    
    uint8_t available() const { return rx_count_; }
};

int main() {
    // Create sensors
    std::cout << "=== Creating Sensors ===\n";
    Sensor temp_sensor(1, "Temperature");
    Sensor humid_sensor(2, "Humidity", 200);
    
    std::cout << "Total sensors: " << (int)Sensor::sensor_count << "\n";
    
    // Use sensors
    temp_sensor.enable();
    temp_sensor.calibrate(0.5f);
    float val = temp_sensor.read();
    std::cout << "Reading: " << val << "\n";
    temp_sensor.print_info();
    
    // UART
    std::cout << "\n=== UART Driver ===\n";
    UART uart(115200);
    uart.init();
    
    uint8_t data[] = {0x01, 0x02, 0x03};
    uart.send(data, sizeof(data));
    
    // Simulate receiving bytes
    uart.push_rx(0xAA);
    uart.push_rx(0xBB);
    
    std::cout << "Available bytes: " << (int)uart.available() << "\n";
    
    uint8_t byte;
    while (uart.pop_rx(byte)) {
        std::cout << "RX: 0x" << std::hex << (int)byte << "\n";
    }
    
    return 0;  // Destructors called automatically here!
}
```

---

## 7. Constructors and Destructors

```cpp
/* constructors.cpp - Construction and RAII */

#include <iostream>
#include <cstdint>
#include <cstring>

// ================================================================
// RAII PATTERN
// Resource Acquisition Is Initialization
// The most important C++ pattern!
// Acquire resources in constructor, release in destructor
// Guaranteed cleanup even when exceptions occur!
// ================================================================

class MemoryBuffer {
private:
    uint8_t  *data_;
    uint32_t  size_;
    uint32_t  capacity_;

public:
    // ── DEFAULT CONSTRUCTOR ──────────────────────────────────────
    MemoryBuffer()
        : data_(nullptr), size_(0), capacity_(0)
    {
        std::cout << "Default constructor\n";
    }
    
    // ── PARAMETERIZED CONSTRUCTOR ────────────────────────────────
    explicit MemoryBuffer(uint32_t capacity)
        : size_(0), capacity_(capacity)
    {
        data_ = new uint8_t[capacity];  // Allocate in constructor
        if (data_ == nullptr) {
            capacity_ = 0;
            throw std::bad_alloc();    // Throw on failure
        }
        memset(data_, 0, capacity);
        std::cout << "Created buffer: " << capacity << " bytes\n";
    }
    
    // ── COPY CONSTRUCTOR (deep copy!) ────────────────────────────
    MemoryBuffer(const MemoryBuffer &other)
        : size_(other.size_), capacity_(other.capacity_)
    {
        data_ = new uint8_t[capacity_];
        memcpy(data_, other.data_, size_);  // Copy data!
        std::cout << "Copy constructor\n";
    }
    
    // ── MOVE CONSTRUCTOR (C++11 - efficient!) ────────────────────
    MemoryBuffer(MemoryBuffer &&other) noexcept
        : data_(other.data_),       // Steal resources
          size_(other.size_),
          capacity_(other.capacity_)
    {
        other.data_     = nullptr;  // Leave source empty
        other.size_     = 0;
        other.capacity_ = 0;
        std::cout << "Move constructor\n";
    }
    
    // ── COPY ASSIGNMENT ──────────────────────────────────────────
    MemoryBuffer& operator=(const MemoryBuffer &other) {
        if (this != &other) {  // Self-assignment check!
            delete[] data_;    // Release old resource
            
            capacity_ = other.capacity_;
            size_     = other.size_;
            data_     = new uint8_t[capacity_];
            memcpy(data_, other.data_, size_);
        }
        return *this;
    }
    
    // ── DESTRUCTOR (RAII - guaranteed cleanup!) ──────────────────
    ~MemoryBuffer() {
        delete[] data_;   // Free memory (safe to delete nullptr)
        data_ = nullptr;
        std::cout << "Buffer destroyed\n";
    }
    
    // ── METHODS ─────────────────────────────────────────────────
    bool write(const uint8_t *data, uint32_t len) {
        if (size_ + len > capacity_) return false;
        memcpy(data_ + size_, data, len);
        size_ += len;
        return true;
    }
    
    bool read(uint8_t *out, uint32_t len) {
        if (len > size_) return false;
        memcpy(out, data_, len);
        memmove(data_, data_ + len, size_ - len);
        size_ -= len;
        return true;
    }
    
    uint32_t size()     const { return size_; }
    uint32_t capacity() const { return capacity_; }
    bool     empty()    const { return size_ == 0; }
    
    void print() const {
        std::cout << "Buffer[" << size_ << "/" << capacity_ << "]: ";
        for (uint32_t i = 0; i < size_; i++) {
            std::cout << std::hex << "0x" << (int)data_[i] << " ";
        }
        std::cout << "\n";
    }
};

// ================================================================
// FILE RAII WRAPPER
// ================================================================
class FileGuard {
private:
    FILE *fp_;

public:
    FileGuard(const char *filename, const char *mode)
        : fp_(fopen(filename, mode))
    {
        if (fp_ == nullptr) {
            throw std::runtime_error("Failed to open file");
        }
        std::cout << "File opened: " << filename << "\n";
    }
    
    ~FileGuard() {
        if (fp_ != nullptr) {
            fclose(fp_);
            std::cout << "File closed automatically\n";
        }
    }
    
    // Delete copy (files shouldn't be copied)
    FileGuard(const FileGuard&) = delete;
    FileGuard& operator=(const FileGuard&) = delete;
    
    FILE* get() { return fp_; }
    bool valid() const { return fp_ != nullptr; }
};

int main() {
    // Default constructor
    MemoryBuffer empty_buf;
    
    // Parameterized constructor
    MemoryBuffer buf(256);
    
    // Write data
    uint8_t data[] = {0x01, 0x02, 0x03, 0x04};
    buf.write(data, sizeof(data));
    buf.print();
    
    // Copy constructor
    MemoryBuffer copy_buf = buf;
    copy_buf.print();
    
    // Move constructor (efficient - no copy!)
    MemoryBuffer moved_buf = std::move(buf);
    // buf is now empty (moved from)
    moved_buf.print();
    
    // RAII: FileGuard automatically closes file!
    try {
        FileGuard file("test.txt", "w");
        fprintf(file.get(), "Hello from FileGuard!\n");
        // File closes automatically here (destructor called)
    } catch (const std::exception &e) {
        std::cout << "Error: " << e.what() << "\n";
    }
    // File is GUARANTEED to be closed here!
    
    return 0;
    // All MemoryBuffers freed here automatically!
}
```

---

## 8. Inheritance

```cpp
/* inheritance.cpp - Class hierarchy */

#include <iostream>
#include <cstdint>
#include <string>
#include <cmath>

// ================================================================
// BASE CLASS (abstract hardware device)
// ================================================================
class Device {
protected:
    uint8_t     address_;
    std::string name_;
    bool        initialized_;

public:
    Device(uint8_t address, const std::string &name)
        : address_(address), name_(name), initialized_(false)
    {
        std::cout << "Device created: " << name_ << " @ 0x" 
                  << std::hex << (int)address_ << "\n";
    }
    
    virtual ~Device() {
        std::cout << "Device destroyed: " << name_ << "\n";
    }
    
    virtual bool init() = 0;  // Pure virtual - MUST override!
    
    virtual void reset() {
        initialized_ = false;
        std::cout << name_ << " reset\n";
    }
    
    bool is_initialized() const { return initialized_; }
    const std::string& get_name() const { return name_; }
    uint8_t get_address() const { return address_; }
};

// ================================================================
// SPI DEVICE BASE CLASS (intermediate level)
// ================================================================
class SPIDevice : public Device {
protected:
    uint32_t spi_freq_;
    uint8_t  cs_pin_;

public:
    SPIDevice(uint8_t address, const std::string &name,
              uint32_t freq, uint8_t cs_pin)
        : Device(address, name),  // Call parent constructor!
          spi_freq_(freq), cs_pin_(cs_pin)
    {}
    
    bool init() override {
        // Initialize SPI bus
        std::cout << "SPI init: " << spi_freq_ / 1000000 << " MHz, CS=" << (int)cs_pin_ << "\n";
        initialized_ = true;
        return true;
    }
    
    virtual uint8_t read_register(uint8_t reg) {
        // Simulate SPI read
        return reg * 2;
    }
    
    virtual void write_register(uint8_t reg, uint8_t val) {
        std::cout << "SPI write reg 0x" << std::hex << (int)reg 
                  << " = 0x" << (int)val << "\n";
    }
};

// ================================================================
// CONCRETE CLASS: ADXL362 Accelerometer
// ================================================================
class ADXL362 : public SPIDevice {
private:
    float   scale_x_, scale_y_, scale_z_;
    uint8_t range_;  // ±2g, ±4g, ±8g
    
    // Register addresses
    static const uint8_t REG_DEVID       = 0x00;
    static const uint8_t REG_POWER_CTL   = 0x2D;
    static const uint8_t REG_XDATA_L     = 0x0E;
    static const uint8_t REG_RANGE       = 0x31;

public:
    enum Range { RANGE_2G = 2, RANGE_4G = 4, RANGE_8G = 8 };
    
    ADXL362(uint8_t cs_pin = 5)
        : SPIDevice(0x1D, "ADXL362", 8000000, cs_pin),
          scale_x_(0), scale_y_(0), scale_z_(0), range_(2)
    {}
    
    bool init() override {
        // Call parent init first
        if (!SPIDevice::init()) return false;
        
        // Check device ID
        uint8_t id = read_register(REG_DEVID);
        std::cout << "ADXL362 ID: 0x" << std::hex << (int)id << "\n";
        
        // Configure measurement mode
        write_register(REG_POWER_CTL, 0x02);  // Measurement mode
        
        initialized_ = true;
        std::cout << "ADXL362 initialized\n";
        return true;
    }
    
    void set_range(Range range) {
        range_ = range;
        float lsb_per_g = 1.0f;
        switch (range) {
            case RANGE_2G: lsb_per_g = 1024; break;
            case RANGE_4G: lsb_per_g = 512;  break;
            case RANGE_8G: lsb_per_g = 256;  break;
        }
        write_register(REG_RANGE, range);
    }
    
    struct AccelData {
        float x, y, z;
        float magnitude() const {
            return sqrt(x*x + y*y + z*z);
        }
    };
    
    AccelData read_accel() {
        // Simulate reading (real code would read registers)
        AccelData data;
        data.x = 0.1f;
        data.y = -0.2f;
        data.z = 9.81f;  // Gravity!
        return data;
    }
    
    void print_accel() {
        AccelData data = read_accel();
        std::cout << "ADXL362 Accel:\n";
        std::cout << "  X: " << data.x << " g\n";
        std::cout << "  Y: " << data.y << " g\n";
        std::cout << "  Z: " << data.z << " g\n";
        std::cout << "  |G|: " << data.magnitude() << " g\n";
    }
};

// ================================================================
// ANOTHER CONCRETE CLASS: SHT31 Temperature/Humidity
// ================================================================
class SHT31 : public Device {
private:
    float temperature_;
    float humidity_;

public:
    SHT31(uint8_t address = 0x44)
        : Device(address, "SHT31"),
          temperature_(0), humidity_(0)
    {}
    
    bool init() override {
        std::cout << "SHT31 init at 0x" << std::hex << (int)address_ << "\n";
        initialized_ = true;
        return true;
    }
    
    bool read() {
        if (!initialized_) return false;
        // Simulate reading
        temperature_ = 25.5f;
        humidity_    = 60.0f;
        return true;
    }
    
    float get_temperature() const { return temperature_; }
    float get_humidity()    const { return humidity_; }
};

int main() {
    // Polymorphism through base pointer
    std::cout << "=== Device Init ===\n";
    ADXL362 accel;
    SHT31   temp_humid;
    
    Device *devices[] = {&accel, &temp_humid};
    uint8_t device_count = 2;
    
    // Initialize all devices polymorphically
    for (uint8_t i = 0; i < device_count; i++) {
        std::cout << "\nInitializing: " << devices[i]->get_name() << "\n";
        devices[i]->init();
    }
    
    // Use specific device
    std::cout << "\n=== Sensor Readings ===\n";
    accel.set_range(ADXL362::RANGE_4G);
    accel.print_accel();
    
    temp_humid.read();
    std::cout << "Temperature: " << temp_humid.get_temperature() << "°C\n";
    std::cout << "Humidity: " << temp_humid.get_humidity() << "%\n";
    
    return 0;
}
```

---

## 9. Polymorphism and Virtual Functions

```cpp
/* polymorphism.cpp - Virtual functions, interfaces */

#include <iostream>
#include <cstdint>
#include <memory>
#include <vector>
#include <string>

// ================================================================
// PURE ABSTRACT INTERFACE (like Java interface)
// ================================================================
class ISensor {
public:
    virtual ~ISensor() = default;
    
    virtual bool  init()                 = 0;  // Pure virtual
    virtual float read()                 = 0;  // Pure virtual
    virtual bool  is_ready()    const    = 0;  // Pure virtual
    virtual std::string get_name() const = 0;  // Pure virtual
};

// ================================================================
// INTERFACE IMPLEMENTATIONS
// ================================================================
class TemperatureSensor : public ISensor {
private:
    float value_;
    bool  ready_;
    
public:
    TemperatureSensor() : value_(0), ready_(false) {}
    
    bool init() override {
        ready_ = true;
        std::cout << "TemperatureSensor initialized\n";
        return true;
    }
    
    float read() override {
        value_ = 25.5f;  // Simulate reading
        return value_;
    }
    
    bool is_ready() const override { return ready_; }
    
    std::string get_name() const override { return "Temperature"; }
};

class PressureSensor : public ISensor {
private:
    float value_;
    bool  ready_;
    
public:
    PressureSensor() : value_(0), ready_(false) {}
    
    bool init() override {
        ready_ = true;
        std::cout << "PressureSensor initialized\n";
        return true;
    }
    
    float read() override {
        value_ = 1013.25f;  // Standard pressure (hPa)
        return value_;
    }
    
    bool is_ready() const override { return ready_; }
    
    std::string get_name() const override { return "Pressure"; }
};

// ================================================================
// VIRTUAL DISPATCH (runtime polymorphism)
// ================================================================
void init_all_sensors(std::vector<ISensor*> &sensors) {
    for (auto *sensor : sensors) {
        sensor->init();  // Calls correct init for each type!
    }
}

void read_all_sensors(const std::vector<ISensor*> &sensors) {
    for (const auto *sensor : sensors) {
        if (sensor->is_ready()) {
            std::cout << sensor->get_name() << ": " << sensor->read() << "\n";
        }
    }
}

// ================================================================
// VTABLE EXPLANATION
// ================================================================
/*
 When class has virtual functions, compiler creates vtable:
 
 ISensor vtable:
 +----------+
 | init()   | → &TemperatureSensor::init()
 | read()   | → &TemperatureSensor::read()
 | is_ready | → &TemperatureSensor::is_ready()
 | get_name | → &TemperatureSensor::get_name()
 +----------+
 
 Each object has a hidden pointer to its vtable.
 Virtual call: obj->vtable[function_index]()
 
 Cost: One extra pointer per object + one indirection per call
 Usually worth it! Can avoid with templates (CRTP pattern)
*/

// ================================================================
// CRTP (Curiously Recurring Template Pattern)
// Static polymorphism - zero runtime cost!
// ================================================================
template<typename Derived>
class SensorBase {
public:
    bool init()   { return static_cast<Derived*>(this)->init_impl(); }
    float read()  { return static_cast<Derived*>(this)->read_impl(); }
    
    void process() {
        if (init()) {
            float val = read();
            std::cout << "Value: " << val << "\n";
        }
    }
};

class AnalogSensor : public SensorBase<AnalogSensor> {
public:
    bool  init_impl()  { std::cout << "Analog init\n"; return true; }
    float read_impl()  { return 3.3f * 512 / 1024; }  // 12-bit ADC
};

int main() {
    // Polymorphic sensor array
    TemperatureSensor temp;
    PressureSensor    pressure;
    
    std::vector<ISensor*> sensors = {&temp, &pressure};
    
    std::cout << "=== Initialize All ===\n";
    init_all_sensors(sensors);
    
    std::cout << "\n=== Read All ===\n";
    read_all_sensors(sensors);
    
    // CRTP (zero-cost)
    std::cout << "\n=== CRTP Sensor ===\n";
    AnalogSensor analog;
    analog.process();
    
    return 0;
}
```

---

## 10. Operator Overloading

```cpp
/* operators.cpp - Custom operators */

#include <iostream>
#include <cstdint>
#include <cmath>

// ================================================================
// VECTOR3 CLASS (useful for sensor fusion, robotics)
// ================================================================
class Vector3 {
public:
    float x, y, z;
    
    Vector3(float x = 0, float y = 0, float z = 0)
        : x(x), y(y), z(z) {}
    
    // Arithmetic operators
    Vector3 operator+(const Vector3 &rhs) const {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    
    Vector3 operator-(const Vector3 &rhs) const {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
    
    Vector3 operator*(float scalar) const {
        return {x * scalar, y * scalar, z * scalar};
    }
    
    float operator*(const Vector3 &rhs) const {  // Dot product
        return x * rhs.x + y * rhs.y + z * rhs.z;
    }
    
    // Compound assignment
    Vector3& operator+=(const Vector3 &rhs) {
        x += rhs.x; y += rhs.y; z += rhs.z;
        return *this;
    }
    
    // Comparison
    bool operator==(const Vector3 &rhs) const {
        const float eps = 0.0001f;
        return fabsf(x - rhs.x) < eps &&
               fabsf(y - rhs.y) < eps &&
               fabsf(z - rhs.z) < eps;
    }
    
    bool operator!=(const Vector3 &rhs) const {
        return !(*this == rhs);
    }
    
    // Subscript operator
    float& operator[](uint8_t idx) {
        if (idx == 0) return x;
        if (idx == 1) return y;
        return z;
    }
    
    // Output operator (friend function)
    friend std::ostream& operator<<(std::ostream &os, const Vector3 &v) {
        os << "(" << v.x << ", " << v.y << ", " << v.z << ")";
        return os;
    }
    
    // Utility methods
    float magnitude() const { return sqrtf(x*x + y*y + z*z); }
    
    Vector3 normalize() const {
        float mag = magnitude();
        if (mag < 0.0001f) return {0, 0, 0};
        return {x/mag, y/mag, z/mag};
    }
    
    Vector3 cross(const Vector3 &rhs) const {
        return {
            y * rhs.z - z * rhs.y,
            z * rhs.x - x * rhs.z,
            x * rhs.y - y * rhs.x
        };
    }
};

// Scalar * Vector (non-member)
Vector3 operator*(float scalar, const Vector3 &v) {
    return v * scalar;
}

int main() {
    Vector3 accel(0.1f, -0.2f, 9.81f);   // Accelerometer reading
    Vector3 gravity(0.0f, 0.0f, 9.81f);   // Gravity vector
    
    // Arithmetic
    Vector3 linear_accel = accel - gravity;  // Remove gravity
    std::cout << "Linear accel: " << linear_accel << "\n";
    
    Vector3 scaled = accel * 2.0f;
    std::cout << "Scaled: " << scaled << "\n";
    
    // Dot product (angle between vectors)
    float dot = accel * gravity;
    std::cout << "Dot product: " << dot << "\n";
    
    // Subscript
    std::cout << "X: " << accel[0] << ", Y: " << accel[1] << ", Z: " << accel[2] << "\n";
    
    // Magnitude
    std::cout << "Magnitude: " << accel.magnitude() << "\n";
    
    // Normalize
    Vector3 unit = accel.normalize();
    std::cout << "Unit vector: " << unit << "\n";
    
    return 0;
}
```

---

## 11. Templates

```cpp
/* templates.cpp - Generic programming */

#include <iostream>
#include <cstdint>
#include <stdexcept>

// ================================================================
// FUNCTION TEMPLATES
// ================================================================
template<typename T>
T clamp(T value, T min_val, T max_val) {
    return (value < min_val) ? min_val :
           (value > max_val) ? max_val : value;
}

template<typename T>
T abs_val(T x) {
    return (x < T(0)) ? -x : x;
}

// Specialization for specific type
template<>
float abs_val<float>(float x) {
    return fabsf(x);
}

// ================================================================
// CLASS TEMPLATE: Ring Buffer
// ================================================================
template<typename T, uint16_t SIZE>
class RingBuffer {
private:
    T        buf_[SIZE];
    uint16_t head_;
    uint16_t tail_;
    uint16_t count_;

public:
    RingBuffer() : head_(0), tail_(0), count_(0) {
        static_assert(SIZE > 0 && (SIZE & (SIZE-1)) == 0,
                      "SIZE must be power of 2!");
    }
    
    bool push(const T &item) {
        if (count_ >= SIZE) return false;
        buf_[head_] = item;
        head_ = (head_ + 1) & (SIZE - 1);  // Fast modulo for pow2!
        count_++;
        return true;
    }
    
    bool pop(T &item) {
        if (count_ == 0) return false;
        item = buf_[tail_];
        tail_ = (tail_ + 1) & (SIZE - 1);
        count_--;
        return true;
    }
    
    bool peek(T &item) const {
        if (count_ == 0) return false;
        item = buf_[tail_];
        return true;
    }
    
    uint16_t count()    const { return count_; }
    uint16_t capacity() const { return SIZE; }
    bool     empty()    const { return count_ == 0; }
    bool     full()     const { return count_ == SIZE; }
    
    void clear() { head_ = tail_ = count_ = 0; }
};

// ================================================================
// TEMPLATE: Statistics calculator
// ================================================================
template<typename T, uint16_t N>
class Statistics {
private:
    T data_[N];
    uint16_t count_;

public:
    Statistics() : count_(0) {}
    
    void add(T value) {
        if (count_ < N) {
            data_[count_++] = value;
        }
    }
    
    float mean() const {
        if (count_ == 0) return 0;
        float sum = 0;
        for (uint16_t i = 0; i < count_; i++) sum += data_[i];
        return sum / count_;
    }
    
    T min() const {
        T m = data_[0];
        for (uint16_t i = 1; i < count_; i++) if (data_[i] < m) m = data_[i];
        return m;
    }
    
    T max() const {
        T m = data_[0];
        for (uint16_t i = 1; i < count_; i++) if (data_[i] > m) m = data_[i];
        return m;
    }
    
    float variance() const {
        float m = mean();
        float sum = 0;
        for (uint16_t i = 0; i < count_; i++) {
            float diff = data_[i] - m;
            sum += diff * diff;
        }
        return sum / count_;
    }
    
    float std_dev() const { return sqrtf(variance()); }
};

int main() {
    // Function templates
    std::cout << "clamp<int>(15, 0, 10) = " << clamp<int>(15, 0, 10) << "\n";
    std::cout << "clamp<float>(1.5f, 0, 1) = " << clamp(1.5f, 0.0f, 1.0f) << "\n";
    std::cout << "abs_val(-5) = " << abs_val(-5) << "\n";
    std::cout << "abs_val(-3.14f) = " << abs_val(-3.14f) << "\n";
    
    // Ring buffer with uint8_t
    std::cout << "\n=== uint8_t Ring Buffer ===\n";
    RingBuffer<uint8_t, 8> byte_buf;
    
    for (uint8_t i = 0; i < 5; i++) byte_buf.push(i * 10);
    std::cout << "Count: " << byte_buf.count() << "\n";
    
    uint8_t val;
    while (byte_buf.pop(val)) std::cout << (int)val << " ";
    std::cout << "\n";
    
    // Ring buffer with struct
    struct SensorPacket {
        uint32_t timestamp;
        float    value;
    };
    
    RingBuffer<SensorPacket, 16> packet_buf;
    packet_buf.push({1000, 25.5f});
    packet_buf.push({2000, 26.1f});
    
    SensorPacket pkt;
    while (packet_buf.pop(pkt)) {
        std::cout << "t=" << pkt.timestamp << " v=" << pkt.value << "\n";
    }
    
    // Statistics
    std::cout << "\n=== Statistics ===\n";
    Statistics<float, 100> stats;
    float sensor_readings[] = {25.1f, 25.3f, 24.9f, 25.5f, 25.2f};
    
    for (float r : sensor_readings) stats.add(r);
    
    std::cout << "Mean: " << stats.mean() << "\n";
    std::cout << "Min: "  << stats.min()  << "\n";
    std::cout << "Max: "  << stats.max()  << "\n";
    std::cout << "Std dev: " << stats.std_dev() << "\n";
    
    return 0;
}
```

---

## 12. Standard Template Library (STL)

```cpp
/* stl.cpp - STL containers and algorithms */

#include <iostream>
#include <vector>
#include <array>
#include <map>
#include <unordered_map>
#include <set>
#include <queue>
#include <stack>
#include <algorithm>
#include <numeric>
#include <functional>
#include <string>
#include <cstdint>

int main() {
    
    // ================================================================
    // ARRAY (fixed-size, stack allocated - great for embedded!)
    // ================================================================
    std::cout << "=== std::array ===\n";
    std::array<uint8_t, 8> registers = {0x01, 0x02, 0x03, 0x04,
                                         0x05, 0x06, 0x07, 0x08};
    
    std::cout << "Size: " << registers.size() << "\n";
    std::cout << "First: 0x" << std::hex << (int)registers.front() << "\n";
    std::cout << "Last: 0x"  << (int)registers.back() << std::dec << "\n";
    
    // ================================================================
    // VECTOR (dynamic array, heap allocated)
    // ================================================================
    std::cout << "\n=== std::vector ===\n";
    std::vector<float> sensor_data;
    sensor_data.reserve(100);  // Pre-allocate (avoid reallocations)
    
    // Add data
    for (int i = 0; i < 10; i++) {
        sensor_data.push_back(i * 1.5f);
    }
    
    std::cout << "Size: " << sensor_data.size() << "\n";
    std::cout << "Capacity: " << sensor_data.capacity() << "\n";
    
    // Access
    std::cout << "Index 3: " << sensor_data[3] << "\n";        // No bounds check
    std::cout << "At 3: "    << sensor_data.at(3) << "\n";     // With bounds check
    
    // Iterate
    for (const auto &val : sensor_data) {
        std::cout << val << " ";
    }
    std::cout << "\n";
    
    // Remove element
    sensor_data.erase(sensor_data.begin() + 5);  // Remove index 5
    
    // ================================================================
    // MAP (sorted key-value pairs)
    // ================================================================
    std::cout << "\n=== std::map ===\n";
    std::map<std::string, float> config;
    config["temperature_scale"] = 0.01f;
    config["voltage_ref"] = 3.3f;
    config["sample_rate"] = 100.0f;
    
    // Access
    std::cout << "voltage_ref: " << config["voltage_ref"] << "\n";
    
    // Check if key exists
    if (config.count("temperature_scale") > 0) {
        std::cout << "temp_scale found: " << config["temperature_scale"] << "\n";
    }
    
    // Iterate
    for (const auto &[key, value] : config) {  // Structured binding (C++17)
        std::cout << key << " = " << value << "\n";
    }
    
    // ================================================================
    // UNORDERED_MAP (hash map - O(1) lookup, faster than map)
    // ================================================================
    std::cout << "\n=== std::unordered_map ===\n";
    std::unordered_map<uint8_t, std::string> register_names;
    register_names[0x00] = "DEVID";
    register_names[0x2D] = "POWER_CTL";
    register_names[0x31] = "DATA_FORMAT";
    
    uint8_t reg = 0x2D;
    auto it = register_names.find(reg);
    if (it != register_names.end()) {
        std::cout << "Reg 0x" << std::hex << (int)reg 
                  << " = " << it->second << "\n";
    }
    
    // ================================================================
    // ALGORITHMS
    // ================================================================
    std::cout << std::dec << "\n=== Algorithms ===\n";
    std::vector<int> nums = {5, 2, 8, 1, 9, 3, 7, 4, 6};
    
    // Sort
    std::sort(nums.begin(), nums.end());
    std::cout << "Sorted: ";
    for (int n : nums) std::cout << n << " ";
    std::cout << "\n";
    
    // Find
    auto found = std::find(nums.begin(), nums.end(), 7);
    if (found != nums.end()) {
        std::cout << "Found 7 at index: " << (found - nums.begin()) << "\n";
    }
    
    // Min/max
    auto [min_it, max_it] = std::minmax_element(nums.begin(), nums.end());
    std::cout << "Min: " << *min_it << ", Max: " << *max_it << "\n";
    
    // Accumulate (sum)
    int sum = std::accumulate(nums.begin(), nums.end(), 0);
    std::cout << "Sum: " << sum << "\n";
    
    // Count if
    int even_count = std::count_if(nums.begin(), nums.end(),
                                   [](int n) { return n % 2 == 0; });
    std::cout << "Even count: " << even_count << "\n";
    
    // Transform (apply function to each element)
    std::vector<float> sensor_readings = {100, 200, 150, 175};
    std::vector<float> voltages(sensor_readings.size());
    std::transform(sensor_readings.begin(), sensor_readings.end(),
                   voltages.begin(),
                   [](float raw) { return raw * 3.3f / 1024.0f; });
    
    std::cout << "Voltages: ";
    for (float v : voltages) std::cout << v << " ";
    std::cout << "\n";
    
    // ================================================================
    // QUEUE (FIFO - useful for message queues!)
    // ================================================================
    std::cout << "\n=== std::queue ===\n";
    std::queue<uint8_t> uart_rx;
    
    // Fill queue
    for (uint8_t b : {0xAA, 0xBB, 0xCC, 0xDD}) uart_rx.push(b);
    
    // Process queue (FIFO order)
    while (!uart_rx.empty()) {
        std::cout << "0x" << std::hex << (int)uart_rx.front() << " ";
        uart_rx.pop();
    }
    std::cout << "\n";
    
    // ================================================================
    // STACK (LIFO - undo operations, call stack simulation)
    // ================================================================
    std::cout << std::dec << "\n=== std::stack ===\n";
    std::stack<std::string> command_history;
    command_history.push("init");
    command_history.push("start");
    command_history.push("measure");
    
    while (!command_history.empty()) {
        std::cout << "Undo: " << command_history.top() << "\n";
        command_history.pop();
    }
    
    return 0;
}
```

---

## 13. Exception Handling

```cpp
/* exceptions.cpp - Error handling with exceptions */

#include <iostream>
#include <stdexcept>
#include <string>
#include <cstdint>

// ================================================================
// CUSTOM EXCEPTIONS
// ================================================================
class HardwareException : public std::exception {
private:
    std::string message_;
    uint8_t     error_code_;

public:
    HardwareException(const std::string &msg, uint8_t code)
        : message_(msg), error_code_(code) {}
    
    const char* what() const noexcept override {
        return message_.c_str();
    }
    
    uint8_t error_code() const { return error_code_; }
};

class SensorException : public HardwareException {
public:
    SensorException(const std::string &msg)
        : HardwareException(msg, 0x01) {}
};

class CommunicationException : public HardwareException {
public:
    CommunicationException(const std::string &msg)
        : HardwareException(msg, 0x02) {}
};

// ================================================================
// FUNCTIONS THAT THROW
// ================================================================
float read_sensor_value(uint8_t channel) {
    if (channel > 7) {
        throw std::out_of_range("Channel must be 0-7");
    }
    if (channel == 3) {
        throw SensorException("Sensor disconnected on channel 3");
    }
    return channel * 0.5f;
}

void init_communication(const char *port) {
    if (port == nullptr) {
        throw std::invalid_argument("Port cannot be null");
    }
    if (std::string(port) == "FAIL") {
        throw CommunicationException("Cannot open port: " + std::string(port));
    }
    std::cout << "Communication initialized on " << port << "\n";
}

// ================================================================
// NOEXCEPT (guarantee no exceptions thrown)
// Important for embedded! Tells compiler to optimize better
// ================================================================
uint32_t safe_add(uint32_t a, uint32_t b) noexcept {
    return a + b;  // Cannot throw
}

int main() {
    // Basic try-catch
    std::cout << "=== Basic Exception ===\n";
    try {
        float val = read_sensor_value(2);   // OK
        std::cout << "Channel 2: " << val << "\n";
        
        float bad = read_sensor_value(10);  // Throws!
    }
    catch (const std::out_of_range &e) {
        std::cout << "Range error: " << e.what() << "\n";
    }
    catch (const SensorException &e) {
        std::cout << "Sensor error [" << (int)e.error_code() 
                  << "]: " << e.what() << "\n";
    }
    catch (const HardwareException &e) {
        std::cout << "Hardware error: " << e.what() << "\n";
    }
    catch (const std::exception &e) {
        std::cout << "Error: " << e.what() << "\n";
    }
    
    // Multiple catches
    std::cout << "\n=== Multiple Catches ===\n";
    for (uint8_t ch = 0; ch < 5; ch++) {
        try {
            float val = read_sensor_value(ch);
            std::cout << "CH" << (int)ch << ": " << val << "\n";
        }
        catch (const SensorException &e) {
            std::cout << "CH" << (int)ch << " ERROR: " << e.what() << "\n";
        }
    }
    
    // Communication exception
    std::cout << "\n=== Communication ===\n";
    try {
        init_communication("/dev/ttyUSB0");
        init_communication("FAIL");  // Will throw
    }
    catch (const CommunicationException &e) {
        std::cout << "Comm error: " << e.what() << "\n";
    }
    
    return 0;
}
```

---

## 14. Smart Pointers

```cpp
/* smart_pointers.cpp - Modern memory management */

#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <cstdint>

// ================================================================
// WHY SMART POINTERS?
// ================================================================
// Raw pointer problems:
//   - Forget to free → Memory leak
//   - Free twice → Crash
//   - Use after free → Undefined behavior
//   - Exception safety → Leak if exception thrown
//
// Smart pointers: RAII for heap memory
//   - Auto-freed when out of scope
//   - Exception safe
//   - Ownership semantics clear

// ================================================================
// UNIQUE_PTR: Single ownership (most common)
// ================================================================
class SensorDriver {
private:
    std::string name_;
    uint8_t     id_;

public:
    SensorDriver(const std::string &name, uint8_t id)
        : name_(name), id_(id)
    {
        std::cout << "SensorDriver created: " << name_ << "\n";
    }
    
    ~SensorDriver() {
        std::cout << "SensorDriver destroyed: " << name_ << "\n";
    }
    
    float read() { return id_ * 1.5f; }
    const std::string& name() const { return name_; }
};

// ================================================================
// SHARED_PTR: Shared ownership (reference counted)
// ================================================================
class DeviceManager {
private:
    std::vector<std::shared_ptr<SensorDriver>> sensors_;

public:
    void add_sensor(std::shared_ptr<SensorDriver> sensor) {
        sensors_.push_back(sensor);
        std::cout << "Added: " << sensor->name() << "\n";
    }
    
    void read_all() {
        for (auto &sensor : sensors_) {
            std::cout << sensor->name() << ": " << sensor->read() << "\n";
        }
    }
    
    uint8_t count() const { return sensors_.size(); }
};

int main() {
    // ── UNIQUE_PTR ──────────────────────────────────────────────
    std::cout << "=== unique_ptr ===\n";
    {
        // Create unique_ptr (preferred way)
        auto driver = std::make_unique<SensorDriver>("ADXL362", 1);
        
        // Use it like a regular pointer
        std::cout << "Reading: " << driver->read() << "\n";
        
        // Transfer ownership (move semantics)
        auto driver2 = std::move(driver);  // driver is now nullptr!
        
        if (driver == nullptr) {
            std::cout << "driver is null after move\n";
        }
        std::cout << "driver2 reading: " << driver2->read() << "\n";
        
    }  // driver2 automatically freed here!
    std::cout << "After scope: memory freed!\n";
    
    // ── SHARED_PTR ──────────────────────────────────────────────
    std::cout << "\n=== shared_ptr ===\n";
    {
        DeviceManager manager;
        
        // Create shared sensors
        auto temp   = std::make_shared<SensorDriver>("Temperature", 1);
        auto humid  = std::make_shared<SensorDriver>("Humidity", 2);
        auto press  = std::make_shared<SensorDriver>("Pressure", 3);
        
        manager.add_sensor(temp);
        manager.add_sensor(humid);
        manager.add_sensor(press);
        
        // Both manager and local variables share ownership
        std::cout << "temp use_count: " << temp.use_count() << "\n";  // 2
        
        manager.read_all();
        
    }  // All sensors freed when manager destroyed and local ptrs go out of scope
    
    // ── UNIQUE_PTR with ARRAY ────────────────────────────────────
    std::cout << "\n=== unique_ptr array ===\n";
    {
        // Preferred way to allocate arrays on heap!
        auto buffer = std::make_unique<uint8_t[]>(256);
        
        // Use it
        for (int i = 0; i < 10; i++) buffer[i] = i;
        for (int i = 0; i < 10; i++) std::cout << (int)buffer[i] << " ";
        std::cout << "\n";
    }  // buffer freed automatically!
    
    return 0;
}
```

---

## 15. Modern C++ Features (C++11/14/17)

```cpp
/* modern_cpp.cpp - C++11/14/17 features */

#include <iostream>
#include <optional>      // C++17
#include <variant>       // C++17
#include <tuple>
#include <chrono>
#include <functional>
#include <numeric>
#include <algorithm>
#include <cstdint>
#include <string>
#include <vector>

// ================================================================
// OPTIONAL (C++17) - May or may not have a value
// Better than returning -1 or using out parameters!
// ================================================================
std::optional<float> read_sensor(uint8_t channel) {
    if (channel > 7) return std::nullopt;  // No value
    return channel * 3.3f / 7;             // Has value
}

// ================================================================
// STRUCTURED BINDINGS (C++17) - Unpack tuple/struct
// ================================================================
std::tuple<float, float, float> read_imu() {
    return {0.1f, -0.2f, 9.81f};  // Return multiple values!
}

struct MinMax { float min, max; };

MinMax find_min_max(const std::vector<float> &data) {
    auto [it_min, it_max] = std::minmax_element(data.begin(), data.end());
    return {*it_min, *it_max};
}

// ================================================================
// VARIANT (C++17) - Type-safe union
// ================================================================
using SensorValue = std::variant<int, float, bool, std::string>;

void process_sensor_value(const SensorValue &val) {
    std::visit([](const auto &v) {
        std::cout << "Value: " << v << "\n";
    }, val);
}

// ================================================================
// CHRONO - Time measurement
// ================================================================
template<typename Func, typename... Args>
auto time_function(Func func, Args&&... args) {
    auto start = std::chrono::high_resolution_clock::now();
    auto result = func(std::forward<Args>(args)...);
    auto end = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
        end - start).count();
    std::cout << "Took: " << duration << " µs\n";
    return result;
}

// ================================================================
// IF CONSTEXPR (C++17) - Compile-time branching
// ================================================================
template<typename T>
void print_type_info(T val) {
    if constexpr (std::is_integral_v<T>) {
        std::cout << "Integer: " << val << " (hex: 0x" << std::hex << val << ")\n";
    } else if constexpr (std::is_floating_point_v<T>) {
        std::cout << std::dec << "Float: " << val << "\n";
    } else {
        std::cout << "Other: " << val << "\n";
    }
}

int main() {
    // optional
    std::cout << "=== optional ===\n";
    auto val = read_sensor(3);
    if (val.has_value()) {
        std::cout << "Sensor: " << val.value() << "\n";
    }
    
    auto bad = read_sensor(10);
    std::cout << "Bad channel: " << (bad.has_value() ? "has value" : "no value") << "\n";
    
    // value_or: default if no value
    std::cout << "With default: " << bad.value_or(-1.0f) << "\n";
    
    // Structured bindings
    std::cout << "\n=== Structured Bindings ===\n";
    auto [x, y, z] = read_imu();
    std::cout << "X=" << x << " Y=" << y << " Z=" << z << "\n";
    
    std::vector<float> data = {5.1f, 2.3f, 8.7f, 1.2f, 9.4f};
    auto [mn, mx] = find_min_max(data);
    std::cout << "Min=" << mn << " Max=" << mx << "\n";
    
    // Variant
    std::cout << "\n=== Variant ===\n";
    std::vector<SensorValue> readings;
    readings.push_back(42);           // int
    readings.push_back(3.14f);        // float
    readings.push_back(true);         // bool
    readings.push_back(std::string("OK"));  // string
    
    for (const auto &r : readings) process_sensor_value(r);
    
    // if constexpr
    std::cout << "\n=== if constexpr ===\n";
    print_type_info(42);
    print_type_info(3.14f);
    print_type_info(std::string("hello"));
    
    // Chrono timing
    std::cout << "\n=== Chrono ===\n";
    auto timed_result = time_function([]{
        volatile int sum = 0;
        for (int i = 0; i < 1000000; i++) sum += i;
        return sum;
    });
    std::cout << "Result: " << timed_result << "\n";
    
    return 0;
}
```

---

## 16. Embedded C++ Patterns

```cpp
/* embedded_cpp.cpp - C++ patterns for embedded systems */

#include <iostream>
#include <cstdint>
#include <cstring>
#include <array>
#include <functional>
#include <type_traits>

// ================================================================
// HARDWARE REGISTER ABSTRACTION (type-safe!)
// ================================================================
template<uint32_t ADDRESS, typename T = uint32_t>
class Register {
public:
    static T read() {
        return *reinterpret_cast<volatile T*>(ADDRESS);
    }
    
    static void write(T val) {
        *reinterpret_cast<volatile T*>(ADDRESS) = val;
    }
    
    static void set_bits(T mask) {
        write(read() | mask);
    }
    
    static void clear_bits(T mask) {
        write(read() & ~mask);
    }
    
    static void toggle_bits(T mask) {
        write(read() ^ mask);
    }
    
    static bool check_bit(uint8_t bit) {
        return (read() >> bit) & 1;
    }
};

// Define hardware registers (simulation)
// using GPIOA_ODR = Register<0x40020014>;
// GPIOA_ODR::set_bits(1 << 5);  // Set pin 5

// ================================================================
// GPIO ABSTRACTION (type-safe, zero-overhead)
// ================================================================
enum class PinMode   { Input, Output, AlternateFunction, Analog };
enum class PinState  { Low = 0, High = 1 };
enum class PullMode  { None, Up, Down };

template<uint8_t PIN_NUM>
class GPIO {
    static_assert(PIN_NUM < 16, "PIN_NUM must be < 16");
    
public:
    static void set_mode(PinMode mode) {
        std::cout << "GPIO[" << (int)PIN_NUM << "] mode set\n";
    }
    
    static void write(PinState state) {
        std::cout << "GPIO[" << (int)PIN_NUM << "] = " 
                  << (state == PinState::High ? "HIGH" : "LOW") << "\n";
    }
    
    static PinState read() {
        return PinState::Low;  // Simulate
    }
    
    static void toggle() {
        std::cout << "GPIO[" << (int)PIN_NUM << "] toggled\n";
    }
};

// Usage:
// GPIO<5>::set_mode(PinMode::Output);
// GPIO<5>::write(PinState::High);

// ================================================================
// OBSERVER PATTERN (event callbacks)
// ================================================================
template<typename EventType, uint8_t MAX_OBSERVERS = 8>
class EventBus {
public:
    using Handler = std::function<void(const EventType&)>;
    
private:
    Handler  handlers_[MAX_OBSERVERS];
    uint8_t  count_ = 0;

public:
    bool subscribe(Handler handler) {
        if (count_ >= MAX_OBSERVERS) return false;
        handlers_[count_++] = handler;
        return true;
    }
    
    void publish(const EventType &event) {
        for (uint8_t i = 0; i < count_; i++) {
            handlers_[i](event);
        }
    }
};

// ================================================================
// SINGLETON (one global hardware instance)
// ================================================================
class SystemClock {
private:
    uint32_t frequency_;
    
    SystemClock() : frequency_(168000000) {}  // Private constructor
    
public:
    static SystemClock& instance() {
        static SystemClock clock;  // Created once, on first call
        return clock;
    }
    
    // Delete copy/move
    SystemClock(const SystemClock&) = delete;
    SystemClock& operator=(const SystemClock&) = delete;
    
    uint32_t get_frequency() const { return frequency_; }
    void set_frequency(uint32_t freq) { frequency_ = freq; }
};

// ================================================================
// COMMAND PATTERN (for command processing)
// ================================================================
struct Command {
    uint8_t opcode;
    uint8_t data[7];
    uint8_t checksum;
};

class CommandProcessor {
public:
    using Handler = std::function<void(const Command&)>;
    
private:
    static const uint8_t MAX_COMMANDS = 16;
    uint8_t  opcodes_[MAX_COMMANDS];
    Handler  handlers_[MAX_COMMANDS];
    uint8_t  count_ = 0;

public:
    bool register_handler(uint8_t opcode, Handler handler) {
        if (count_ >= MAX_COMMANDS) return false;
        opcodes_[count_] = opcode;
        handlers_[count_] = handler;
        count_++;
        return true;
    }
    
    bool process(const Command &cmd) {
        for (uint8_t i = 0; i < count_; i++) {
            if (opcodes_[i] == cmd.opcode) {
                handlers_[i](cmd);
                return true;
            }
        }
        std::cout << "Unknown opcode: 0x" << std::hex << (int)cmd.opcode << "\n";
        return false;
    }
};

struct ButtonEvent {
    uint8_t pin;
    bool    pressed;
};

int main() {
    // GPIO (compile-time pin numbers!)
    std::cout << "=== GPIO ===\n";
    GPIO<5>::set_mode(PinMode::Output);
    GPIO<5>::write(PinState::High);
    GPIO<5>::toggle();
    
    // Event bus
    std::cout << "\n=== Event Bus ===\n";
    EventBus<ButtonEvent> button_bus;
    
    button_bus.subscribe([](const ButtonEvent &e) {
        std::cout << "Handler 1: pin=" << (int)e.pin 
                  << (e.pressed ? " pressed" : " released") << "\n";
    });
    
    button_bus.subscribe([](const ButtonEvent &e) {
        std::cout << "Handler 2: LED " 
                  << (e.pressed ? "ON" : "OFF") << "\n";
    });
    
    button_bus.publish({5, true});
    button_bus.publish({5, false});
    
    // Singleton
    std::cout << "\n=== Singleton ===\n";
    auto &clk = SystemClock::instance();
    std::cout << "Clock: " << clk.get_frequency() / 1000000 << " MHz\n";
    
    // Same instance everywhere
    auto &clk2 = SystemClock::instance();
    clk2.set_frequency(216000000);
    std::cout << "Updated clock: " << clk.get_frequency() / 1000000 << " MHz\n";
    
    // Command processor
    std::cout << "\n=== Command Processor ===\n";
    CommandProcessor proc;
    
    proc.register_handler(0x01, [](const Command &c) {
        std::cout << "INIT command\n";
    });
    
    proc.register_handler(0x02, [](const Command &c) {
        std::cout << "READ command\n";
    });
    
    Command cmd1 = {0x01, {0}, 0};
    Command cmd2 = {0x02, {0}, 0};
    Command cmd3 = {0xFF, {0}, 0};
    
    proc.process(cmd1);
    proc.process(cmd2);
    proc.process(cmd3);
    
    return 0;
}
```

---

## 17. Best Practices

```cpp
/* best_practices.cpp - C++ do's and don'ts */

#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <cstdint>
#include <cassert>

// ================================================================
// RULE OF ZERO/THREE/FIVE
// ================================================================
// Rule of Zero:  If no special management needed, define nothing
// Rule of Three: If you define destructor, copy ctor, or copy =,
//                define all three
// Rule of Five:  Add move ctor and move = to rule of three (C++11)

// ================================================================
// BAD vs GOOD EXAMPLES
// ================================================================

// BAD: Raw pointers for ownership
class BadBuffer {
    uint8_t *data;
    uint32_t size;
public:
    BadBuffer(uint32_t sz) : data(new uint8_t[sz]), size(sz) {}
    ~BadBuffer() { delete[] data; }
    // Missing: copy ctor, copy =, move ctor, move =
    // COPY WILL DOUBLE-FREE!
};

// GOOD: RAII with rule of five
class GoodBuffer {
    std::unique_ptr<uint8_t[]> data_;
    uint32_t size_;
public:
    explicit GoodBuffer(uint32_t sz)
        : data_(std::make_unique<uint8_t[]>(sz)), size_(sz)
    {}
    
    // Rule of five: explicitly defaulted/deleted
    GoodBuffer(const GoodBuffer &other)
        : data_(std::make_unique<uint8_t[]>(other.size_)),
          size_(other.size_)
    {
        std::copy(other.data_.get(), other.data_.get() + size_,
                  data_.get());
    }
    
    GoodBuffer(GoodBuffer &&other)     = default;
    GoodBuffer& operator=(GoodBuffer&&) = default;
    GoodBuffer& operator=(const GoodBuffer&) = delete;  // Explicit!
    ~GoodBuffer() = default;  // unique_ptr handles it
};

// ================================================================
// PREFER ALGORITHMS TO LOOPS
// ================================================================
#include <algorithm>
#include <numeric>

void process_data(std::vector<float> &data) {
    // BAD: Manual loop
    float sum_bad = 0;
    for (uint32_t i = 0; i < data.size(); i++) {
        sum_bad += data[i];
    }
    
    // GOOD: STL algorithm
    float sum_good = std::accumulate(data.begin(), data.end(), 0.0f);
    
    // BAD: Manual find
    bool found_bad = false;
    for (float v : data) {
        if (v > 100.0f) { found_bad = true; break; }
    }
    
    // GOOD: STL algorithm
    bool found_good = std::any_of(data.begin(), data.end(),
                                  [](float v) { return v > 100.0f; });
}

// ================================================================
// CONST CORRECTNESS
// ================================================================
class Sensor {
    float value_;
    
public:
    Sensor(float v) : value_(v) {}
    
    // GOOD: const member functions for read-only operations
    float get_value() const { return value_; }  // const - doesn't modify
    void  set_value(float v) { value_ = v; }    // non-const - modifies
    
    // GOOD: const reference parameter for large objects
    void process(const std::vector<float> &data) const {
        // data cannot be modified
        // this->value_ cannot be modified (const member func)
    }
};

// ================================================================
// USE STRONGLY TYPED ENUMS
// ================================================================
// BAD: old style enum (pollutes namespace)
enum OldMode { INPUT, OUTPUT, ANALOG };

// GOOD: enum class (scoped, strongly typed)
enum class Mode { Input, Output, Analog };

void set_mode(Mode mode) {
    switch (mode) {
        case Mode::Input:   std::cout << "Input mode\n";  break;
        case Mode::Output:  std::cout << "Output mode\n"; break;
        case Mode::Analog:  std::cout << "Analog mode\n"; break;
    }
}

// ================================================================
// EXPLICIT CONSTRUCTORS
// ================================================================
class Voltage {
    float volts_;
public:
    explicit Voltage(float v) : volts_(v) {}  // explicit: no implicit conversion
    float get() const { return volts_; }
};

// Without explicit: Voltage v = 3.3f;  would work (confusing!)
// With explicit:    Voltage v(3.3f);   must be explicit

// ================================================================
// CONSTEXPR EVERYWHERE
// ================================================================
constexpr float PI = 3.14159265f;
constexpr uint32_t SYS_CLOCK_HZ = 168000000;
constexpr uint32_t TIMER_FREQ_HZ = 1000;
constexpr uint32_t PRESCALER = SYS_CLOCK_HZ / TIMER_FREQ_HZ - 1;
// All computed at compile time! Zero runtime cost.

int main() {
    // Strongly typed enum
    set_mode(Mode::Output);
    // set_mode(OUTPUT);  ERROR - old enum not accepted!
    
    // Explicit constructor
    Voltage v(3.3f);
    std::cout << "Voltage: " << v.get() << "V\n";
    
    // Constexpr values
    std::cout << "Prescaler: " << PRESCALER << "\n";  // Compile-time computed
    
    // RAII - no manual cleanup
    {
        GoodBuffer buf(256);
        // Use buf...
    }  // Automatically freed - no memory leak!
    
    std::cout << "All done - no leaks!\n";
    return 0;
}
```

---

## Compilation Flags Reference

```bash
# Development (all warnings, debug)
g++ -Wall -Wextra -Wpedantic -g -std=c++17 file.cpp -o program

# Release (optimized)
g++ -O2 -std=c++17 -DNDEBUG file.cpp -o program

# With sanitizers (detect bugs!)
g++ -Wall -g -std=c++17 -fsanitize=address,undefined file.cpp -o program

# Embedded (ARM Cortex-M4)
arm-none-eabi-g++ -mcpu=cortex-m4 -mthumb -O2 -std=c++17 \
    -fno-exceptions -fno-rtti file.cpp -o program.elf

# Flags for embedded (no exceptions, no RTTI saves space!)
# -fno-exceptions  : Disable exception handling (saves ~5-10KB)
# -fno-rtti        : Disable runtime type info (saves ~1-2KB)
# -ffunction-sections -fdata-sections : Put each in separate section
# -Wl,--gc-sections : Linker removes unused sections!

# Check object sizes
arm-none-eabi-size program.elf
# Shows: text (flash) + data (RAM initialized) + bss (RAM zeroed)
```

---

## Quick Reference Card

```cpp
// TYPES (use fixed-width for embedded!)
uint8_t u8;  uint16_t u16;  uint32_t u32;  uint64_t u64;
int8_t  s8;  int16_t  s16;  int32_t  s32;  int64_t  s64;
auto x = 42;  // Type deduced as int

// I/O
std::cout << value << "\n";
std::cin >> variable;

// REFERENCES
int &ref = var;          // Reference (alias)
const int &cref = var;   // Const reference (no copy)

// CLASSES
class Foo {
public:
    Foo(int x) : x_(x) {}   // Constructor with init list
    ~Foo() {}                 // Destructor
    int get_x() const { return x_; }  // Const method
private:
    int x_;
};

// INHERITANCE
class Bar : public Foo {
public:
    Bar(int x) : Foo(x) {}  // Call parent constructor
    void func() override {}   // Override virtual
};

// TEMPLATES
template<typename T>  T func(T x)   { return x; }
template<typename T, int N>  class Fixed {};

// SMART POINTERS
auto up = std::make_unique<T>(args);  // Unique ownership
auto sp = std::make_shared<T>(args);  // Shared ownership

// STL
std::vector<T> v;    v.push_back(x);
std::array<T,N> a;   a[i];
std::map<K,V> m;     m[key] = val;

// ALGORITHMS
std::sort(v.begin(), v.end());
std::find(v.begin(), v.end(), val);
std::for_each(v.begin(), v.end(), func);
float sum = std::accumulate(v.begin(), v.end(), 0.0f);

// LAMBDAS
auto fn = [](int x, int y) { return x + y; };
auto cap = [&var](int x) { return x + var; };  // Capture by reference

// MODERN C++
std::optional<T> opt = val;   opt.value_or(default);
auto [a, b, c] = my_tuple;   // Structured binding (C++17)
if constexpr (condition) {}  // Compile-time if (C++17)
```
