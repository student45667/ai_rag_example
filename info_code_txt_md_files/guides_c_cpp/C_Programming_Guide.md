# C Programming - Comprehensive Guide for Engineers and Developers

## Who This Guide Is For

This guide targets:
- **Embedded systems engineers** working with microcontrollers (AVR, STM32, ESP32)
- **Firmware developers** writing low-level hardware drivers
- **Systems programmers** building operating systems, compilers, tools
- **C++ developers** wanting to understand C foundations

**Assumed knowledge:** Basic programming concepts (variables, loops, functions)

---

## Table of Contents

1. [Introduction to C](#1-introduction-to-c)
2. [Setup and Compilation](#2-setup-and-compilation)
3. [Data Types and Variables](#3-data-types-and-variables)
4. [Operators](#4-operators)
5. [Control Flow](#5-control-flow)
6. [Functions](#6-functions)
7. [Arrays](#7-arrays)
8. [Pointers and Memory](#8-pointers-and-memory)
9. [Strings](#9-strings)
10. [Structures and Unions](#10-structures-and-unions)
11. [Dynamic Memory Allocation](#11-dynamic-memory-allocation)
12. [File I/O](#12-file-io)
13. [Preprocessor Directives](#13-preprocessor-directives)
14. [Bit Manipulation](#14-bit-manipulation)
15. [Advanced Topics](#15-advanced-topics)
16. [Embedded Systems Patterns](#16-embedded-systems-patterns)
17. [Common Mistakes and Best Practices](#17-common-mistakes-and-best-practices)

---

## 1. Introduction to C

### What is C?

C is a **general-purpose, procedural programming language** created by Dennis Ritchie at Bell Labs in 1972. It is:

- **Low-level**: Direct access to memory and hardware
- **Fast**: Compiled to machine code, minimal overhead
- **Portable**: Runs on virtually any processor
- **Foundational**: Linux kernel, Python interpreter, SQLite all written in C

### Why C for Engineers?

```
Hardware registers → Memory-mapped I/O → C pointers
Interrupts        → Direct hardware access → C function pointers
Real-time         → No garbage collector → C manual memory management
Resource limited  → No runtime overhead → C minimal footprint
```

### The C Standard

```c
/* Different C standards - know which you're using */
// C89/C90 - Original ANSI C (embedded standard)
// C99     - Added inline, stdint.h, bool (most common)
// C11     - Added threads, atomics (modern systems)
// C17     - Bug fixes to C11 (latest stable)

// Compile with specific standard:
// gcc -std=c99 program.c -o program
// gcc -std=c11 program.c -o program
```

---

## 2. Setup and Compilation

### Install GCC Compiler

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential gdb

# Verify installation
gcc --version
# gcc (Ubuntu 11.3.0) 11.3.0

# Install additional tools
sudo apt install valgrind     # Memory leak checker
sudo apt install cppcheck     # Static analysis
```

### Compilation Process

Understanding compilation is critical for embedded work:

```bash
# Full compilation pipeline:

# Step 1: Preprocessing (.c → .i)
# Handles #include, #define, #ifdef
gcc -E main.c -o main.i

# Step 2: Compilation (.i → .s)
# C code → Assembly language
gcc -S main.i -o main.s

# Step 3: Assembly (.s → .o)
# Assembly → machine code (object file)
gcc -c main.s -o main.o

# Step 4: Linking (.o → executable)
# Combines object files with libraries
gcc main.o -o program

# All at once (most common):
gcc main.c -o program

# With warnings and debugging (ALWAYS use these):
gcc -Wall -Wextra -g -std=c99 main.c -o program
```

### Your First Program

```c
/* hello.c - Example 1: Hello World */

#include <stdio.h>    /* Standard I/O library */
#include <stdlib.h>   /* Standard library */

int main(void) {      /* main: entry point of every C program */
                      /* void: takes no arguments */
                      /* int: returns integer (exit code) */
    
    printf("Hello, Engineer!\n");  /* printf: formatted print */
                                   /* \n: newline character */
    
    return 0;   /* 0: success (convention) */
                /* non-zero: error */
}
```

```bash
# Compile and run
gcc -Wall -std=c99 hello.c -o hello
./hello
# Hello, Engineer!
```

### Example 2: Program with Arguments

```c
/* args.c - Reading command-line arguments */

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    /* argc: argument count (always >= 1, program name counts) */
    /* argv: argument vector (array of strings) */
    /* argv[0]: program name */
    /* argv[1]: first argument */
    
    printf("Program name: %s\n", argv[0]);
    printf("Number of arguments: %d\n", argc - 1);
    
    /* Print all arguments */
    for (int i = 1; i < argc; i++) {
        printf("Argument %d: %s\n", i, argv[i]);
    }
    
    /* Check for required arguments */
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <filename>\n", argv[0]);
        return EXIT_FAILURE;   /* EXIT_FAILURE = 1 */
    }
    
    return EXIT_SUCCESS;   /* EXIT_SUCCESS = 0 */
}
```

```bash
gcc -Wall -std=c99 args.c -o args
./args file1.txt file2.txt
# Program name: ./args
# Number of arguments: 2
# Argument 1: file1.txt
# Argument 2: file2.txt
```

---

## 3. Data Types and Variables

### Fundamental Types

```c
/* types.c - Data types for engineers */

#include <stdio.h>
#include <stdint.h>    /* Fixed-width types - CRITICAL for embedded! */
#include <stdbool.h>   /* bool type (C99) */
#include <limits.h>    /* Type limits */
#include <float.h>     /* Float limits */

int main(void) {
    
    /* ================================================================
     * STANDARD TYPES (size depends on platform - avoid for embedded!)
     * ================================================================ */
    char    c = 'A';         /* 1 byte, character */
    int     i = 42;          /* Usually 4 bytes (platform-dependent!) */
    float   f = 3.14f;       /* 4 bytes, single precision */
    double  d = 3.14159265;  /* 8 bytes, double precision */
    long    l = 1000000L;    /* 4 or 8 bytes (platform-dependent!) */
    
    /* ================================================================
     * FIXED-WIDTH TYPES (use these for embedded/portable code!)
     * ================================================================ */
    uint8_t  byte_val  = 255;         /* Exactly 8 bits, unsigned */
    int8_t   signed8   = -128;        /* Exactly 8 bits, signed */
    uint16_t word_val  = 65535;       /* Exactly 16 bits, unsigned */
    int16_t  signed16  = -32768;      /* Exactly 16 bits, signed */
    uint32_t dword_val = 4294967295U; /* Exactly 32 bits, unsigned */
    int32_t  signed32  = -2147483648; /* Exactly 32 bits, signed */
    uint64_t qword_val = 18446744073709551615ULL; /* Exactly 64 bits */
    
    /* ================================================================
     * BOOL TYPE (C99)
     * ================================================================ */
    bool flag = true;     /* true = 1, false = 0 */
    bool done = false;
    
    /* ================================================================
     * TYPE SIZES (platform-dependent for standard types!)
     * ================================================================ */
    printf("char:    %zu bytes\n", sizeof(char));      /* 1 */
    printf("int:     %zu bytes\n", sizeof(int));       /* 4 (usually) */
    printf("long:    %zu bytes\n", sizeof(long));      /* 4 or 8! */
    printf("float:   %zu bytes\n", sizeof(float));     /* 4 */
    printf("double:  %zu bytes\n", sizeof(double));    /* 8 */
    printf("uint8_t: %zu bytes\n", sizeof(uint8_t));   /* Always 1! */
    printf("uint32_t:%zu bytes\n", sizeof(uint32_t));  /* Always 4! */
    
    /* ================================================================
     * PRINTING FIXED-WIDTH TYPES
     * ================================================================ */
    #include <inttypes.h>   /* For PRIu8, PRId32, etc. */
    printf("uint8:  %" PRIu8  "\n", byte_val);
    printf("int32:  %" PRId32 "\n", signed32);
    printf("uint64: %" PRIu64 "\n", qword_val);
    
    /* ================================================================
     * TYPE RANGES
     * ================================================================ */
    printf("uint8_t range:  0 to %u\n", UINT8_MAX);    /* 0 to 255 */
    printf("int8_t range:   %d to %d\n", INT8_MIN, INT8_MAX); /* -128 to 127 */
    printf("uint32_t range: 0 to %u\n", UINT32_MAX);
    
    return 0;
}
```

### Example 2: Type Casting

```c
/* casting.c - Type conversions (critical for embedded!) */

#include <stdio.h>
#include <stdint.h>

int main(void) {
    
    /* IMPLICIT CASTING (automatic, can be dangerous!) */
    int   a = 300;
    uint8_t b = a;   /* OVERFLOW! 300 > 255, b becomes 44 (300 % 256) */
    printf("Overflow: a=%d, b=%u\n", a, b);   /* a=300, b=44 */
    
    /* EXPLICIT CASTING (intentional, clear intent) */
    double result = 7.0 / 2;            /* 3.5 */
    int    truncated = (int)(7.0 / 2);  /* 3 - explicitly truncated */
    printf("Division: %f, truncated: %d\n", result, truncated);
    
    /* CASTING IN EXPRESSIONS */
    int x = 7;
    int y = 2;
    
    double wrong   = x / y;           /* 3.0! Integer division first */
    double correct = (double)x / y;   /* 3.5 - cast before division */
    printf("Wrong: %f, Correct: %f\n", wrong, correct);
    
    /* SIGN EXTENSION (common embedded bug) */
    int8_t  negative = -1;            /* 0xFF in binary */
    uint8_t unsigned_val = negative;  /* Still 0xFF = 255 as uint8_t */
    int32_t sign_extended = negative; /* 0xFFFFFFFF = -1 (sign extended!) */
    
    printf("int8: %d, uint8: %u, int32: %d\n", 
           negative, unsigned_val, sign_extended);
    
    return 0;
}
```

### Example 3: Constants and Qualifiers

```c
/* constants.c - const, volatile, static, extern */

#include <stdio.h>
#include <stdint.h>

/* GLOBAL CONSTANTS (visible everywhere in file) */
#define MAX_BUFFER_SIZE  256    /* Preprocessor constant - no type! */
#define PI               3.14159265f

/* Better: typed constants */
const uint32_t BAUD_RATE = 115200;
const uint8_t  MAX_RETRIES = 3;

/* REGISTER SIMULATION (volatile example) */
/* volatile: tells compiler not to optimize - CRITICAL for hardware registers! */
volatile uint32_t *const UART_DATA_REG = (uint32_t *)0x40013800;
/* Without volatile: compiler might cache the register value - BUG! */
/* With volatile: always reads from actual hardware address */

/* STATIC: keeps value between function calls */
void count_calls(void) {
    static uint32_t call_count = 0;  /* Initialized once, persists */
    call_count++;
    printf("Called %u times\n", call_count);
}

/* EXTERN: declares variable defined in another file */
/* extern int shared_value; */

int main(void) {
    /* const: cannot be modified after initialization */
    const int TIMEOUT_MS = 1000;
    /* TIMEOUT_MS = 2000;  ERROR! Cannot modify const */
    
    printf("Buffer size: %d\n", MAX_BUFFER_SIZE);
    printf("PI: %f\n", PI);
    printf("Baud rate: %u\n", BAUD_RATE);
    printf("Timeout: %d ms\n", TIMEOUT_MS);
    
    count_calls();  /* Called 1 times */
    count_calls();  /* Called 2 times */
    count_calls();  /* Called 3 times */
    
    return 0;
}
```

---

## 4. Operators

### Arithmetic and Comparison

```c
/* operators.c - All C operators */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

int main(void) {
    
    /* ARITHMETIC OPERATORS */
    int a = 10, b = 3;
    printf("a + b = %d\n", a + b);   /* 13 */
    printf("a - b = %d\n", a - b);   /* 7 */
    printf("a * b = %d\n", a * b);   /* 30 */
    printf("a / b = %d\n", a / b);   /* 3 (integer division!) */
    printf("a %% b = %d\n", a % b);  /* 1 (remainder/modulo) */
    
    /* INCREMENT/DECREMENT */
    int x = 5;
    printf("x++: %d\n", x++);  /* 5 (post: use then increment) */
    printf("x:   %d\n", x);    /* 6 */
    printf("++x: %d\n", ++x);  /* 7 (pre: increment then use) */
    
    /* COMPOUND ASSIGNMENT */
    int val = 10;
    val += 5;   /* val = val + 5 = 15 */
    val -= 3;   /* val = val - 3 = 12 */
    val *= 2;   /* val = val * 2 = 24 */
    val /= 4;   /* val = val / 4 = 6 */
    val %= 4;   /* val = val % 4 = 2 */
    printf("val after operations: %d\n", val);
    
    /* COMPARISON OPERATORS (return 0 or 1) */
    printf("a == b: %d\n", a == b);   /* 0 (false) */
    printf("a != b: %d\n", a != b);   /* 1 (true) */
    printf("a >  b: %d\n", a >  b);   /* 1 (true) */
    printf("a >= b: %d\n", a >= b);   /* 1 (true) */
    printf("a <  b: %d\n", a <  b);   /* 0 (false) */
    printf("a <= b: %d\n", a <= b);   /* 0 (false) */
    
    /* LOGICAL OPERATORS */
    bool p = true, q = false;
    printf("p && q: %d\n", p && q);   /* 0 - AND */
    printf("p || q: %d\n", p || q);   /* 1 - OR */
    printf("!p:     %d\n", !p);       /* 0 - NOT */
    
    /* TERNARY OPERATOR (condition ? true : false) */
    int max = (a > b) ? a : b;
    printf("max(%d, %d) = %d\n", a, b, max);
    
    /* SIZEOF OPERATOR */
    printf("sizeof(int) = %zu\n", sizeof(int));
    printf("sizeof(double) = %zu\n", sizeof(double));
    
    return 0;
}
```

### Bitwise Operators (Critical for Embedded!)

```c
/* bitwise.c - Bit operations for hardware control */

#include <stdio.h>
#include <stdint.h>

/* Print binary representation */
void print_binary(uint8_t val) {
    for (int i = 7; i >= 0; i--) {
        printf("%d", (val >> i) & 1);
        if (i == 4) printf(" ");  /* Space between nibbles */
    }
    printf(" (0x%02X = %d)\n", val, val);
}

int main(void) {
    uint8_t a = 0b10110100;  /* 180 */
    uint8_t b = 0b01101101;  /* 109 */
    
    /* BITWISE AND (&) - both bits must be 1 */
    printf("a & b = "); print_binary(a & b);   /* 0b00100100 */
    
    /* BITWISE OR (|) - either bit must be 1 */
    printf("a | b = "); print_binary(a | b);   /* 0b11111101 */
    
    /* BITWISE XOR (^) - bits must be different */
    printf("a ^ b = "); print_binary(a ^ b);   /* 0b11011001 */
    
    /* BITWISE NOT (~) - flip all bits */
    printf("~a    = "); print_binary(~a);       /* 0b01001011 */
    
    /* LEFT SHIFT (<<) - multiply by 2^n */
    printf("a<<2  = "); print_binary(a << 2);   /* Shift left 2 */
    
    /* RIGHT SHIFT (>>) - divide by 2^n */
    printf("a>>2  = "); print_binary(a >> 2);   /* Shift right 2 */
    
    /* ================================================================
     * PRACTICAL EMBEDDED PATTERNS
     * ================================================================ */
    
    /* Pattern 1: SET a bit */
    uint8_t reg = 0x00;
    uint8_t bit_num = 3;
    reg |= (1 << bit_num);          /* Set bit 3 */
    printf("\nSet bit 3:    "); print_binary(reg);  /* 0b00001000 */
    
    /* Pattern 2: CLEAR a bit */
    reg &= ~(1 << bit_num);         /* Clear bit 3 */
    printf("Clear bit 3:  "); print_binary(reg);  /* 0b00000000 */
    
    /* Pattern 3: TOGGLE a bit */
    reg = 0xFF;
    reg ^= (1 << bit_num);          /* Toggle bit 3 */
    printf("Toggle bit 3: "); print_binary(reg);  /* 0b11110111 */
    
    /* Pattern 4: CHECK a bit */
    reg = 0b10101010;
    if (reg & (1 << 3)) {
        printf("Bit 3 is SET\n");
    } else {
        printf("Bit 3 is CLEAR\n");
    }
    
    /* Pattern 5: Create BITMASK */
    uint8_t mask = 0x0F;            /* Lower nibble mask */
    uint8_t lower = reg & mask;     /* Extract lower 4 bits */
    uint8_t upper = (reg >> 4) & mask; /* Extract upper 4 bits */
    printf("Lower nibble: "); print_binary(lower);
    printf("Upper nibble: "); print_binary(upper);
    
    return 0;
}
```

---

## 5. Control Flow

### If/Else and Switch

```c
/* control.c - Control flow statements */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Simulate hardware status register */
typedef enum {
    STATUS_OK       = 0x00,
    STATUS_BUSY     = 0x01,
    STATUS_ERROR    = 0x02,
    STATUS_TIMEOUT  = 0x03,
    STATUS_OVERFLOW = 0x04
} DeviceStatus;

const char* status_to_string(DeviceStatus status) {
    switch (status) {
        /* SWITCH: jump table, faster than if-else chain */
        case STATUS_OK:
            return "OK";
        case STATUS_BUSY:
            return "BUSY";
        case STATUS_ERROR:
            return "ERROR";
        case STATUS_TIMEOUT:
            return "TIMEOUT";
        case STATUS_OVERFLOW:
            return "OVERFLOW";
        default:
            return "UNKNOWN";  /* Always include default! */
    }
}

int main(void) {
    /* BASIC IF/ELSE */
    int temperature = 85;
    
    if (temperature > 100) {
        printf("CRITICAL: Temperature too high!\n");
    } else if (temperature > 80) {
        printf("WARNING: Temperature elevated\n");
    } else if (temperature > 60) {
        printf("OK: Normal temperature\n");
    } else {
        printf("LOW: Temperature low\n");
    }
    
    /* SWITCH STATEMENT */
    DeviceStatus status = STATUS_BUSY;
    printf("Status: %s\n", status_to_string(status));
    
    /* SWITCH WITH FALLTHROUGH (intentional!) */
    uint8_t error_code = 2;
    switch (error_code) {
        case 1:
        case 2:
        case 3:
            /* Cases 1, 2, 3 all fall through to same handler */
            printf("Minor error: code %d\n", error_code);
            break;   /* ALWAYS break unless intentional fallthrough */
        case 4:
            printf("Major error: code %d\n", error_code);
            break;
        default:
            printf("Unknown error: %d\n", error_code);
    }
    
    return 0;
}
```

### Loops

```c
/* loops.c - All loop types with practical examples */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

int main(void) {
    
    /* FOR LOOP - known iteration count */
    printf("FOR loop:\n");
    uint8_t buffer[8] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
    
    for (int i = 0; i < 8; i++) {
        printf("buffer[%d] = 0x%02X\n", i, buffer[i]);
    }
    
    /* WHILE LOOP - condition checked before entry */
    printf("\nWHILE loop:\n");
    uint8_t retry_count = 0;
    uint8_t max_retries = 3;
    bool device_ready = false;
    
    while (!device_ready && retry_count < max_retries) {
        printf("Attempt %d: Checking device...\n", retry_count + 1);
        /* Simulate device check */
        retry_count++;
        if (retry_count == 2) device_ready = true;  /* Simulate success */
    }
    
    if (device_ready) {
        printf("Device ready after %d attempts\n", retry_count);
    } else {
        printf("Device failed after %d attempts\n", retry_count);
    }
    
    /* DO-WHILE LOOP - executes at least once */
    printf("\nDO-WHILE loop:\n");
    int input = 0;
    do {
        printf("Processing value: %d\n", input);
        input++;
    } while (input < 3);
    
    /* BREAK and CONTINUE */
    printf("\nBREAK example:\n");
    for (int i = 0; i < 10; i++) {
        if (i == 5) break;          /* Exit loop at 5 */
        printf("%d ", i);
    }
    printf("\n");
    
    printf("CONTINUE example:\n");
    for (int i = 0; i < 10; i++) {
        if (i % 2 == 0) continue;  /* Skip even numbers */
        printf("%d ", i);
    }
    printf("\n");
    
    /* NESTED LOOPS (2D array processing) */
    printf("\nNested loops - 2D array:\n");
    uint8_t matrix[3][3] = {
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };
    
    for (int row = 0; row < 3; row++) {
        for (int col = 0; col < 3; col++) {
            printf("%3d", matrix[row][col]);
        }
        printf("\n");
    }
    
    return 0;
}
```

---

## 6. Functions

### Function Basics and Parameter Passing

```c
/* functions.c - Functions in depth */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* FUNCTION DECLARATION (prototype) - tell compiler what exists */
/* Must be before first use */
float    calculate_celsius(float fahrenheit);
uint32_t calculate_checksum(const uint8_t *data, uint32_t length);
void     swap_values(int *a, int *b);

/* ================================================================
 * EXAMPLE 1: Basic function with return value
 * ================================================================ */
float calculate_celsius(float fahrenheit) {
    /* Formula: C = (F - 32) * 5/9 */
    return (fahrenheit - 32.0f) * 5.0f / 9.0f;
}

/* ================================================================
 * EXAMPLE 2: Multiple return paths and error handling
 * ================================================================ */
typedef enum {
    ERR_NONE    = 0,
    ERR_NULL    = -1,
    ERR_INVALID = -2,
    ERR_OVERFLOW = -3
} ErrorCode;

ErrorCode validate_sensor_data(
    const uint16_t *data,       /* const: won't modify data */
    uint32_t count,
    uint16_t min_val,
    uint16_t max_val,
    float *average_out          /* Output parameter: returns average */
) {
    /* Validate inputs */
    if (data == NULL || average_out == NULL) return ERR_NULL;
    if (count == 0) return ERR_INVALID;
    if (min_val >= max_val) return ERR_INVALID;
    
    /* Process data */
    uint32_t sum = 0;
    for (uint32_t i = 0; i < count; i++) {
        if (data[i] < min_val || data[i] > max_val) {
            printf("Out of range: data[%u] = %u\n", i, data[i]);
            return ERR_INVALID;
        }
        sum += data[i];
        if (sum > UINT32_MAX - data[i]) return ERR_OVERFLOW; /* Overflow check */
    }
    
    *average_out = (float)sum / count;  /* Write result via pointer */
    return ERR_NONE;
}

/* ================================================================
 * EXAMPLE 3: Pass by reference (using pointers)
 * ================================================================ */
void swap_values(int *a, int *b) {
    /* a and b are POINTERS to the actual variables */
    int temp = *a;  /* Dereference: get value at address a */
    *a = *b;        /* Write to address a */
    *b = temp;      /* Write to address b */
}

/* ================================================================
 * EXAMPLE 4: Recursive function
 * ================================================================ */
uint32_t factorial(uint32_t n) {
    if (n == 0 || n == 1) return 1;  /* Base case */
    return n * factorial(n - 1);      /* Recursive case */
}

/* ================================================================
 * EXAMPLE 5: Function pointer (used in callbacks, jump tables)
 * ================================================================ */
typedef void (*EventHandler)(uint8_t event_id);

void handle_gpio_event(uint8_t event_id) {
    printf("GPIO event: %d\n", event_id);
}

void handle_uart_event(uint8_t event_id) {
    printf("UART event: %d\n", event_id);
}

void register_and_call(EventHandler handler, uint8_t event) {
    if (handler != NULL) {
        handler(event);  /* Call function via pointer */
    }
}

/* ================================================================
 * EXAMPLE 6: Checksum calculation (practical embedded function)
 * ================================================================ */
uint32_t calculate_checksum(const uint8_t *data, uint32_t length) {
    uint32_t checksum = 0;
    for (uint32_t i = 0; i < length; i++) {
        checksum += data[i];
    }
    return (~checksum + 1);  /* Two's complement */
}

int main(void) {
    /* Test 1: Basic function */
    float temp_f = 98.6f;
    printf("%.1f°F = %.1f°C\n", temp_f, calculate_celsius(temp_f));
    
    /* Test 2: Function with output parameter */
    uint16_t sensor_data[] = {100, 200, 150, 175, 125};
    float average = 0.0f;
    ErrorCode err = validate_sensor_data(
        sensor_data, 5, 50, 250, &average
    );
    if (err == ERR_NONE) {
        printf("Average: %.2f\n", average);
    } else {
        printf("Error: %d\n", err);
    }
    
    /* Test 3: Swap by reference */
    int x = 10, y = 20;
    printf("Before: x=%d, y=%d\n", x, y);
    swap_values(&x, &y);
    printf("After:  x=%d, y=%d\n", x, y);
    
    /* Test 4: Recursive function */
    printf("5! = %u\n", factorial(5));  /* 120 */
    
    /* Test 5: Function pointers */
    EventHandler handlers[2] = {handle_gpio_event, handle_uart_event};
    register_and_call(handlers[0], 1);  /* GPIO event 1 */
    register_and_call(handlers[1], 2);  /* UART event 2 */
    
    /* Test 6: Checksum */
    uint8_t packet[] = {0x01, 0x02, 0x03, 0x04};
    uint32_t csum = calculate_checksum(packet, 4);
    printf("Checksum: 0x%08X\n", csum);
    
    return 0;
}
```

---

## 7. Arrays

### Array Fundamentals

```c
/* arrays.c - Arrays for practical use */

#include <stdio.h>
#include <stdint.h>
#include <string.h>  /* memset, memcpy */

#define BUFFER_SIZE   256
#define MATRIX_ROWS   3
#define MATRIX_COLS   4

int main(void) {
    
    /* ================================================================
     * 1D ARRAYS
     * ================================================================ */
    
    /* Declaration and initialization */
    uint8_t rx_buffer[BUFFER_SIZE];          /* Uninitialized */
    uint8_t tx_buffer[8] = {0};              /* Zero-initialized */
    int     values[] = {10, 20, 30, 40, 50}; /* Size inferred = 5 */
    
    /* Size of array (only works in same scope!) */
    uint32_t arr_size = sizeof(values) / sizeof(values[0]);
    printf("Array size: %u elements\n", arr_size);
    
    /* Initialize with memset (fastest for large arrays) */
    memset(rx_buffer, 0x00, sizeof(rx_buffer));  /* Fill with zeros */
    memset(tx_buffer, 0xFF, sizeof(tx_buffer));  /* Fill with 0xFF */
    
    /* Access and modify elements */
    for (uint32_t i = 0; i < arr_size; i++) {
        values[i] *= 2;  /* Double each element */
    }
    
    /* ================================================================
     * 2D ARRAYS (matrix)
     * ================================================================ */
    
    /* Declare and initialize 2D array */
    int matrix[MATRIX_ROWS][MATRIX_COLS] = {
        {1,  2,  3,  4},
        {5,  6,  7,  8},
        {9, 10, 11, 12}
    };
    
    /* Access 2D array */
    printf("matrix[1][2] = %d\n", matrix[1][2]);  /* 7 */
    
    /* Iterate 2D array */
    printf("Matrix:\n");
    for (int row = 0; row < MATRIX_ROWS; row++) {
        for (int col = 0; col < MATRIX_COLS; col++) {
            printf("%4d", matrix[row][col]);
        }
        printf("\n");
    }
    
    /* ================================================================
     * ARRAY AS FUNCTION PARAMETER
     * Array decays to pointer when passed to function!
     * ================================================================ */
    
    /* Array in memory is contiguous */
    int arr[5] = {1, 2, 3, 4, 5};
    printf("\nMemory layout:\n");
    for (int i = 0; i < 5; i++) {
        printf("arr[%d] = %d (address: %p)\n", i, arr[i], (void*)&arr[i]);
    }
    /* Note: each address is 4 bytes apart (sizeof int) */
    
    /* ================================================================
     * CIRCULAR BUFFER (practical embedded pattern)
     * ================================================================ */
    #define CIRC_BUFFER_SIZE 8
    uint8_t circ_buf[CIRC_BUFFER_SIZE] = {0};
    uint8_t head = 0;  /* Write position */
    uint8_t tail = 0;  /* Read position */
    uint8_t count = 0; /* Number of items */
    
    /* Write to circular buffer */
    for (uint8_t i = 0; i < 5; i++) {
        if (count < CIRC_BUFFER_SIZE) {
            circ_buf[head] = i * 10;
            head = (head + 1) % CIRC_BUFFER_SIZE;  /* Wrap around */
            count++;
        }
    }
    
    /* Read from circular buffer */
    printf("\nCircular buffer read:\n");
    while (count > 0) {
        printf("%d ", circ_buf[tail]);
        tail = (tail + 1) % CIRC_BUFFER_SIZE;
        count--;
    }
    printf("\n");
    
    return 0;
}
```

---

## 8. Pointers and Memory

### Pointer Fundamentals

```c
/* pointers.c - Pointers (most important C concept!) */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

int main(void) {
    
    /* ================================================================
     * POINTER BASICS
     * ================================================================ */
    int value = 42;
    int *ptr = &value;  /* ptr = address of value */
    /* int*: pointer to int */
    /* &: address-of operator */
    /* *: dereference (get value at address) */
    
    printf("value:    %d\n",   value);   /* 42 */
    printf("&value:   %p\n",   (void*)&value);  /* Memory address */
    printf("ptr:      %p\n",   (void*)ptr);     /* Same address */
    printf("*ptr:     %d\n",   *ptr);    /* 42 - dereferenced */
    
    /* Modify through pointer */
    *ptr = 100;  /* Change value through pointer */
    printf("value after *ptr=100: %d\n", value);  /* 100 */
    
    /* ================================================================
     * POINTER ARITHMETIC
     * ================================================================ */
    int arr[] = {10, 20, 30, 40, 50};
    int *p = arr;  /* Points to first element */
    
    printf("\nPointer arithmetic:\n");
    for (int i = 0; i < 5; i++) {
        printf("*(p+%d) = %d (addr: %p)\n", i, *(p+i), (void*)(p+i));
        /* p+i moves by sizeof(int) bytes (4 bytes on 32-bit) */
    }
    
    /* ================================================================
     * POINTER TO POINTER (double pointer)
     * ================================================================ */
    int x = 5;
    int *ptr1 = &x;      /* Pointer to int */
    int **ptr2 = &ptr1;  /* Pointer to pointer to int */
    
    printf("\nDouble pointer:\n");
    printf("x:      %d\n", x);
    printf("*ptr1:  %d\n", *ptr1);    /* 5 */
    printf("**ptr2: %d\n", **ptr2);   /* 5 */
    
    **ptr2 = 99;  /* Modify x through double pointer */
    printf("x after **ptr2=99: %d\n", x);  /* 99 */
    
    /* ================================================================
     * CONST POINTERS (important for embedded!)
     * ================================================================ */
    int var = 10;
    
    /* Pointer to const int: can change pointer, not value */
    const int *p1 = &var;
    /* *p1 = 20;  ERROR! Cannot modify value through p1 */
    p1 = NULL;    /* OK - can change pointer itself */
    
    /* Const pointer to int: cannot change pointer, can change value */
    int * const p2 = &var;
    *p2 = 20;     /* OK - can modify value */
    /* p2 = NULL;  ERROR! Cannot change pointer */
    
    /* Const pointer to const int: cannot change either */
    const int * const p3 = &var;
    /* *p3 = 30;   ERROR! */
    /* p3 = NULL;  ERROR! */
    
    /* ================================================================
     * NULL POINTER (always check before dereferencing!)
     * ================================================================ */
    int *null_ptr = NULL;  /* Explicitly null */
    
    if (null_ptr != NULL) {
        printf("Value: %d\n", *null_ptr);
    } else {
        printf("Pointer is NULL - safe!\n");
    }
    
    /* ================================================================
     * VOID POINTER (generic pointer)
     * ================================================================ */
    void *generic_ptr;
    
    int    int_val  = 42;
    double dbl_val  = 3.14;
    
    generic_ptr = &int_val;
    printf("\nVoid pointer to int: %d\n", *(int*)generic_ptr);
    
    generic_ptr = &dbl_val;
    printf("Void pointer to double: %f\n", *(double*)generic_ptr);
    
    return 0;
}
```

### Pointers and Functions

```c
/* ptr_functions.c - Pointers with functions */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

/* ================================================================
 * PASSING ARRAYS TO FUNCTIONS
 * Array decays to pointer - size info is LOST!
 * Always pass size separately!
 * ================================================================ */
void print_array(const int *arr, uint32_t size) {
    for (uint32_t i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

void reverse_array(int *arr, uint32_t size) {
    for (uint32_t i = 0; i < size / 2; i++) {
        int temp = arr[i];
        arr[i] = arr[size - 1 - i];
        arr[size - 1 - i] = temp;
    }
}

/* ================================================================
 * RETURNING POINTER FROM FUNCTION
 * DANGER: Never return pointer to local variable!
 * ================================================================ */
int* create_array(uint32_t size) {
    /* Allocate on heap - survives function return */
    int *arr = malloc(size * sizeof(int));
    if (arr == NULL) return NULL;
    
    for (uint32_t i = 0; i < size; i++) {
        arr[i] = i * i;  /* Square numbers */
    }
    return arr;
}

/* ================================================================
 * FUNCTION POINTERS (callbacks, ISR handlers)
 * ================================================================ */
typedef int (*MathFunc)(int, int);  /* Function pointer type */

int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
int mul(int a, int b) { return a * b; }

/* Array of function pointers (jump table) */
MathFunc operations[] = {add, sub, mul};
const char* op_names[] = {"add", "sub", "mul"};

void apply_operation(MathFunc func, int x, int y) {
    printf("Result: %d\n", func(x, y));
}

int main(void) {
    /* Test arrays */
    int arr[] = {1, 2, 3, 4, 5};
    uint32_t size = sizeof(arr) / sizeof(arr[0]);
    
    printf("Original: ");
    print_array(arr, size);
    
    reverse_array(arr, size);
    printf("Reversed: ");
    print_array(arr, size);
    
    /* Test heap array */
    int *heap_arr = create_array(5);
    if (heap_arr != NULL) {
        printf("Heap array: ");
        print_array(heap_arr, 5);
        free(heap_arr);  /* MUST free! */
        heap_arr = NULL; /* Good practice */
    }
    
    /* Test function pointers */
    int x = 10, y = 3;
    
    /* Direct call via pointer */
    MathFunc add_func = add;
    apply_operation(add_func, x, y);   /* Result: 13 */
    
    /* Jump table */
    printf("\nJump table:\n");
    for (int i = 0; i < 3; i++) {
        printf("%s(%d, %d) = %d\n", op_names[i], x, y,
               operations[i](x, y));
    }
    
    return 0;
}
```

---

## 9. Strings

### String Operations

```c
/* strings.c - String handling in C */

#include <stdio.h>
#include <string.h>  /* strlen, strcpy, strcat, strcmp, etc. */
#include <ctype.h>   /* toupper, tolower, isdigit, etc. */
#include <stdlib.h>  /* atoi, atof */
#include <stdint.h>

int main(void) {
    
    /* ================================================================
     * STRING BASICS
     * Strings in C are arrays of char, terminated by '\0' (null)
     * ================================================================ */
    char str1[] = "Hello";        /* Array: {'H','e','l','l','o','\0'} */
    char str2[20] = "World";      /* Fixed size buffer */
    char str3[20];                 /* Uninitialized buffer */
    const char *str4 = "Literal"; /* String literal - READ ONLY! */
    
    printf("str1 length: %zu\n", strlen(str1));  /* 5 (not 6!) */
    printf("str2 size: %zu\n", sizeof(str2));    /* 20 (buffer size) */
    
    /* ================================================================
     * COMMON STRING FUNCTIONS
     * ================================================================ */
    
    /* strlen: string length (excludes null terminator) */
    printf("strlen: %zu\n", strlen(str1));  /* 5 */
    
    /* strcpy: copy string (UNSAFE - use strncpy!) */
    strncpy(str3, str1, sizeof(str3) - 1);  /* Safe copy */
    str3[sizeof(str3) - 1] = '\0';          /* Ensure null-terminated */
    printf("strcpy: %s\n", str3);
    
    /* strcat: concatenate (UNSAFE - use strncat!) */
    char result[40] = "Hello";
    strncat(result, " World", sizeof(result) - strlen(result) - 1);
    printf("strcat: %s\n", result);
    
    /* strcmp: compare strings (returns 0 if equal) */
    if (strcmp(str1, "Hello") == 0) {
        printf("Strings are equal\n");
    }
    
    /* strncmp: compare n characters */
    printf("strncmp: %d\n", strncmp("abc", "abd", 2));  /* 0 (first 2 match) */
    
    /* strchr: find character */
    char *found = strchr("Hello World", 'W');
    if (found) printf("Found 'W' at: %s\n", found);  /* World */
    
    /* strstr: find substring */
    char *sub = strstr("Hello World", "World");
    if (sub) printf("Found 'World': %s\n", sub);
    
    /* ================================================================
     * STRING CONVERSION
     * ================================================================ */
    
    /* String to number */
    const char *num_str = "12345";
    int num_int = atoi(num_str);      /* String to int */
    float num_flt = atof("3.14");    /* String to float */
    long num_long = strtol("0xFF", NULL, 16);  /* Hex string to long */
    printf("atoi: %d, atof: %.2f, strtol: %ld\n", num_int, num_flt, num_long);
    
    /* Number to string */
    char num_buf[32];
    snprintf(num_buf, sizeof(num_buf), "%d", 12345);
    printf("snprintf: %s\n", num_buf);
    
    /* ================================================================
     * STRING PARSING (practical: parse sensor data "T:25.5,H:60.3")
     * ================================================================ */
    char sensor_data[] = "T:25.5,H:60.3";
    char *token;
    float temperature = 0.0f;
    float humidity = 0.0f;
    
    /* Parse with strtok (modifies original string!) */
    token = strtok(sensor_data, ",");
    while (token != NULL) {
        char *colon = strchr(token, ':');
        if (colon != NULL) {
            char key = token[0];
            float val = atof(colon + 1);
            if (key == 'T') temperature = val;
            if (key == 'H') humidity = val;
        }
        token = strtok(NULL, ",");
    }
    printf("Temperature: %.1f°C, Humidity: %.1f%%\n", temperature, humidity);
    
    /* ================================================================
     * CHARACTER FUNCTIONS
     * ================================================================ */
    char mixed[] = "Hello World 123!";
    printf("\nCharacter analysis of '%s':\n", mixed);
    for (int i = 0; mixed[i] != '\0'; i++) {
        if (isalpha(mixed[i])) printf("%c is alpha\n", mixed[i]);
        if (isdigit(mixed[i])) printf("%c is digit\n", mixed[i]);
    }
    
    return 0;
}
```

---

## 10. Structures and Unions

### Structures

```c
/* structures.c - Structures for hardware abstraction */

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

/* ================================================================
 * BASIC STRUCTURE
 * ================================================================ */
typedef struct {
    uint8_t  id;
    char     name[32];
    float    voltage;
    float    current;
    bool     enabled;
} Sensor;

/* ================================================================
 * NESTED STRUCTURE
 * ================================================================ */
typedef struct {
    uint8_t  hour;
    uint8_t  minute;
    uint8_t  second;
} Time;

typedef struct {
    uint16_t year;
    uint8_t  month;
    uint8_t  day;
    Time     time;       /* Nested structure */
} DateTime;

/* ================================================================
 * BIT FIELDS (memory-efficient, hardware register mapping!)
 * ================================================================ */
typedef struct {
    uint8_t power_on    : 1;  /* 1 bit */
    uint8_t sleep_mode  : 1;  /* 1 bit */
    uint8_t data_ready  : 1;  /* 1 bit */
    uint8_t error_flag  : 1;  /* 1 bit */
    uint8_t mode        : 2;  /* 2 bits (0-3) */
    uint8_t reserved    : 2;  /* 2 bits reserved */
} StatusRegister;

/* ================================================================
 * UNION (same memory, different interpretations)
 * Critical for type-punning in embedded!
 * ================================================================ */
typedef union {
    uint32_t raw;          /* Access all 32 bits */
    uint8_t  bytes[4];     /* Access individual bytes */
    struct {               /* Access named fields */
        uint8_t  low_byte;
        uint8_t  high_byte;
        uint16_t upper_word;
    } fields;
} Register32;

/* ================================================================
 * LINKED LIST (dynamic data structure)
 * ================================================================ */
typedef struct Node {
    uint8_t      data;
    struct Node *next;  /* Pointer to next node */
} Node;

/* Functions */
void print_sensor(const Sensor *s) {
    printf("Sensor %d: %s\n", s->id, s->name);
    printf("  Voltage: %.2fV, Current: %.2fA\n", s->voltage, s->current);
    printf("  Enabled: %s\n", s->enabled ? "yes" : "no");
}

void print_datetime(const DateTime *dt) {
    printf("%04d-%02d-%02d %02d:%02d:%02d\n",
           dt->year, dt->month, dt->day,
           dt->time.hour, dt->time.minute, dt->time.second);
}

int main(void) {
    /* Create and initialize structure */
    Sensor sensor1 = {
        .id      = 1,
        .name    = "Temperature",
        .voltage = 3.3f,
        .current = 0.015f,
        .enabled = true
    };
    print_sensor(&sensor1);
    
    /* Access members with dot notation */
    sensor1.voltage = 5.0f;
    
    /* Access members via pointer with -> */
    Sensor *ptr = &sensor1;
    ptr->current = 0.020f;
    print_sensor(ptr);
    
    /* Nested structure */
    DateTime dt = {
        .year  = 2024,
        .month = 5,
        .day   = 1,
        .time  = {.hour = 14, .minute = 30, .second = 0}
    };
    print_datetime(&dt);
    
    /* Bit fields */
    StatusRegister reg = {0};
    reg.power_on   = 1;
    reg.data_ready = 1;
    reg.mode       = 2;   /* Binary 10 */
    printf("\nStatus register:\n");
    printf("  power_on: %d\n", reg.power_on);
    printf("  data_ready: %d\n", reg.data_ready);
    printf("  mode: %d\n", reg.mode);
    printf("  sizeof: %zu bytes\n", sizeof(reg));
    
    /* Union - type punning */
    Register32 r32;
    r32.raw = 0x12345678;
    printf("\nUnion bytes:\n");
    printf("  raw: 0x%08X\n", r32.raw);
    printf("  bytes: %02X %02X %02X %02X\n",
           r32.bytes[0], r32.bytes[1], r32.bytes[2], r32.bytes[3]);
    printf("  low_byte: 0x%02X\n", r32.fields.low_byte);
    printf("  upper_word: 0x%04X\n", r32.fields.upper_word);
    
    return 0;
}
```

---

## 11. Dynamic Memory Allocation

```c
/* dynamic_memory.c - malloc, calloc, realloc, free */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

/* ================================================================
 * BASIC ALLOCATION
 * ================================================================ */

/* Dynamically sized sensor array */
typedef struct {
    uint8_t id;
    float   value;
} SensorReading;

SensorReading* allocate_readings(uint32_t count) {
    /* malloc: allocate uninitialized memory */
    SensorReading *readings = malloc(count * sizeof(SensorReading));
    if (readings == NULL) {
        fprintf(stderr, "Memory allocation failed!\n");
        return NULL;
    }
    return readings;
}

/* ================================================================
 * GROWING BUFFER PATTERN
 * ================================================================ */
typedef struct {
    uint8_t  *data;
    uint32_t  size;
    uint32_t  capacity;
} DynamicBuffer;

DynamicBuffer* buffer_create(uint32_t initial_capacity) {
    DynamicBuffer *buf = malloc(sizeof(DynamicBuffer));
    if (buf == NULL) return NULL;
    
    buf->data = malloc(initial_capacity);
    if (buf->data == NULL) {
        free(buf);
        return NULL;
    }
    
    buf->size = 0;
    buf->capacity = initial_capacity;
    return buf;
}

bool buffer_append(DynamicBuffer *buf, const uint8_t *data, uint32_t len) {
    /* Check if we need to grow */
    if (buf->size + len > buf->capacity) {
        uint32_t new_cap = buf->capacity * 2;
        while (new_cap < buf->size + len) new_cap *= 2;
        
        /* realloc: resize allocation */
        uint8_t *new_data = realloc(buf->data, new_cap);
        if (new_data == NULL) return false;  /* Allocation failed */
        
        buf->data = new_data;
        buf->capacity = new_cap;
    }
    
    memcpy(buf->data + buf->size, data, len);
    buf->size += len;
    return true;
}

void buffer_destroy(DynamicBuffer *buf) {
    if (buf != NULL) {
        free(buf->data);  /* Free inner allocation first */
        buf->data = NULL;
        free(buf);        /* Then free the struct */
    }
}

int main(void) {
    /* malloc example */
    int *arr = malloc(10 * sizeof(int));
    if (arr == NULL) return EXIT_FAILURE;
    
    for (int i = 0; i < 10; i++) arr[i] = i * i;
    for (int i = 0; i < 10; i++) printf("%d ", arr[i]);
    printf("\n");
    
    free(arr);
    arr = NULL;  /* ALWAYS null after free! */
    
    /* calloc: allocate AND zero-initialize */
    int *zeroed = calloc(10, sizeof(int));
    if (zeroed == NULL) return EXIT_FAILURE;
    
    printf("calloc (should be zeros): ");
    for (int i = 0; i < 10; i++) printf("%d ", zeroed[i]);
    printf("\n");
    
    free(zeroed);
    zeroed = NULL;
    
    /* Dynamic buffer example */
    DynamicBuffer *buf = buffer_create(8);
    if (buf == NULL) return EXIT_FAILURE;
    
    uint8_t data1[] = {0x01, 0x02, 0x03, 0x04};
    uint8_t data2[] = {0x05, 0x06, 0x07, 0x08, 0x09, 0x0A};
    
    buffer_append(buf, data1, sizeof(data1));
    buffer_append(buf, data2, sizeof(data2));
    
    printf("Buffer size: %u, capacity: %u\n", buf->size, buf->capacity);
    printf("Buffer data: ");
    for (uint32_t i = 0; i < buf->size; i++) {
        printf("0x%02X ", buf->data[i]);
    }
    printf("\n");
    
    buffer_destroy(buf);
    buf = NULL;
    
    return EXIT_SUCCESS;
}
```

---

## 12. File I/O

```c
/* file_io.c - File operations */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

/* ================================================================
 * WRITE TEXT FILE
 * ================================================================ */
bool write_sensor_log(const char *filename) {
    FILE *fp = fopen(filename, "w");  /* "w" = write (creates or truncates) */
    if (fp == NULL) {
        fprintf(stderr, "Cannot open %s for writing\n", filename);
        return false;
    }
    
    /* Write header */
    fprintf(fp, "Timestamp,Temperature,Humidity\n");
    
    /* Write data */
    for (int i = 0; i < 5; i++) {
        fprintf(fp, "%d,%.1f,%.1f\n",
                i * 1000,
                20.0f + i * 0.5f,
                60.0f + i * 1.0f);
    }
    
    fclose(fp);  /* ALWAYS close! */
    return true;
}

/* ================================================================
 * READ TEXT FILE
 * ================================================================ */
void read_sensor_log(const char *filename) {
    FILE *fp = fopen(filename, "r");  /* "r" = read */
    if (fp == NULL) {
        fprintf(stderr, "Cannot open %s for reading\n", filename);
        return;
    }
    
    char line[256];
    
    /* Read line by line */
    while (fgets(line, sizeof(line), fp) != NULL) {
        /* Remove trailing newline */
        line[strcspn(line, "\n")] = '\0';
        printf("Read: %s\n", line);
    }
    
    fclose(fp);
}

/* ================================================================
 * BINARY FILE (efficient for embedded data logs)
 * ================================================================ */
typedef struct {
    uint32_t timestamp;
    int16_t  temperature;  /* Scaled by 100 e.g. 2550 = 25.50°C */
    uint16_t humidity;     /* Scaled by 100 */
} __attribute__((packed)) SensorRecord;

void write_binary_log(const char *filename) {
    FILE *fp = fopen(filename, "wb");  /* "wb" = write binary */
    if (fp == NULL) return;
    
    SensorRecord records[3] = {
        {1000, 2550, 6030},
        {2000, 2575, 6120},
        {3000, 2600, 6215}
    };
    
    /* Write array of structs at once */
    fwrite(records, sizeof(SensorRecord), 3, fp);
    fclose(fp);
    
    printf("Wrote %zu bytes per record\n", sizeof(SensorRecord));
}

void read_binary_log(const char *filename) {
    FILE *fp = fopen(filename, "rb");  /* "rb" = read binary */
    if (fp == NULL) return;
    
    SensorRecord rec;
    while (fread(&rec, sizeof(SensorRecord), 1, fp) == 1) {
        printf("t=%u, temp=%.2f°C, hum=%.2f%%\n",
               rec.timestamp,
               rec.temperature / 100.0f,
               rec.humidity    / 100.0f);
    }
    
    fclose(fp);
}

int main(void) {
    /* Text file */
    printf("=== Text File ===\n");
    write_sensor_log("sensor_log.csv");
    read_sensor_log("sensor_log.csv");
    
    /* Binary file */
    printf("\n=== Binary File ===\n");
    write_binary_log("sensor_log.bin");
    read_binary_log("sensor_log.bin");
    
    return EXIT_SUCCESS;
}
```

---

## 13. Preprocessor Directives

```c
/* preprocessor.c - Macros and conditional compilation */

#include <stdio.h>
#include <stdint.h>

/* ================================================================
 * MACROS
 * ================================================================ */

/* Object-like macros */
#define VERSION_MAJOR    1
#define VERSION_MINOR    2
#define VERSION_PATCH    3
#define VERSION_STRING   "1.2.3"

/* Function-like macros (always use parentheses!) */
#define MIN(a, b)        ((a) < (b) ? (a) : (b))
#define MAX(a, b)        ((a) > (b) ? (a) : (b))
#define ABS(x)           ((x) < 0 ? -(x) : (x))
#define CLAMP(x, lo, hi) (MIN(MAX((x), (lo)), (hi)))
#define ARRAY_SIZE(arr)  (sizeof(arr) / sizeof((arr)[0]))

/* Bit manipulation macros */
#define BIT(n)           (1U << (n))
#define SET_BIT(reg, n)  ((reg) |=  BIT(n))
#define CLR_BIT(reg, n)  ((reg) &= ~BIT(n))
#define TGL_BIT(reg, n)  ((reg) ^=  BIT(n))
#define CHK_BIT(reg, n)  (((reg) >> (n)) & 1U)

/* Register access macros */
#define REG32(addr)      (*(volatile uint32_t *)(addr))
#define GPIOA_OUT        REG32(0x40010800)

/* Debug macros */
#ifdef DEBUG
    #define DEBUG_PRINT(fmt, ...) \
        fprintf(stderr, "[DEBUG] %s:%d: " fmt "\n", \
                __FILE__, __LINE__, ##__VA_ARGS__)
#else
    #define DEBUG_PRINT(fmt, ...)  /* Empty - compiled out in release! */
#endif

/* Assert macro */
#define ASSERT(cond) \
    do { \
        if (!(cond)) { \
            fprintf(stderr, "ASSERT failed: %s at %s:%d\n", \
                    #cond, __FILE__, __LINE__); \
            while(1);  /* Halt for embedded, or exit for desktop */ \
        } \
    } while(0)

/* ================================================================
 * CONDITIONAL COMPILATION
 * ================================================================ */
#define TARGET_ESP32   /* Define target platform */

#ifdef TARGET_ESP32
    #define GPIO_BASE_ADDR  0x3FF44000
    #define CPU_FREQ_MHZ    240
#elif defined(TARGET_STM32)
    #define GPIO_BASE_ADDR  0x40020000
    #define CPU_FREQ_MHZ    168
#elif defined(TARGET_AVR)
    #define CPU_FREQ_MHZ    16
#else
    #error "Unknown target platform!"
#endif

/* Header guard (prevent double inclusion) */
#ifndef MYHEADER_H
#define MYHEADER_H
/* Header contents here */
#endif

int main(void) {
    printf("Version: %s\n", VERSION_STRING);
    printf("Version: %d.%d.%d\n", VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH);
    
    /* Macro functions */
    printf("MIN(3, 7) = %d\n", MIN(3, 7));  /* 3 */
    printf("MAX(3, 7) = %d\n", MAX(3, 7));  /* 7 */
    printf("ABS(-5) = %d\n", ABS(-5));       /* 5 */
    printf("CLAMP(15, 0, 10) = %d\n", CLAMP(15, 0, 10));  /* 10 */
    
    /* Bit macros */
    uint8_t reg = 0x00;
    SET_BIT(reg, 3);
    printf("After SET_BIT(3): 0x%02X\n", reg);   /* 0x08 */
    SET_BIT(reg, 5);
    printf("After SET_BIT(5): 0x%02X\n", reg);   /* 0x28 */
    CLR_BIT(reg, 3);
    printf("After CLR_BIT(3): 0x%02X\n", reg);   /* 0x20 */
    
    /* Platform info */
    printf("CPU Frequency: %d MHz\n", CPU_FREQ_MHZ);
    
    /* Array size */
    int arr[] = {1, 2, 3, 4, 5};
    printf("Array size: %zu\n", ARRAY_SIZE(arr));  /* 5 */
    
    /* Debug macro */
    DEBUG_PRINT("Value = %d", 42);  /* Only printed if DEBUG defined */
    
    /* Assert */
    ASSERT(sizeof(uint8_t) == 1);   /* Pass */
    /* ASSERT(1 == 0);  This would fail and print error */
    
    return 0;
}
```

---

## 14. Bit Manipulation

```c
/* bit_manipulation.c - Advanced bit operations for embedded */

#include <stdio.h>
#include <stdint.h>

/* ================================================================
 * HARDWARE REGISTER SIMULATION
 * ================================================================ */
typedef struct {
    volatile uint32_t MODER;    /* Mode register */
    volatile uint32_t OTYPER;   /* Output type register */
    volatile uint32_t OSPEEDR;  /* Output speed register */
    volatile uint32_t PUPDR;    /* Pull-up/down register */
    volatile uint32_t IDR;      /* Input data register */
    volatile uint32_t ODR;      /* Output data register */
    volatile uint32_t BSRR;     /* Bit set/reset register */
} GPIO_TypeDef;

/* Bit field positions for MODER register */
#define GPIO_MODER_INPUT    0x00  /* 00 = Input */
#define GPIO_MODER_OUTPUT   0x01  /* 01 = Output */
#define GPIO_MODER_AF       0x02  /* 10 = Alternate function */
#define GPIO_MODER_ANALOG   0x03  /* 11 = Analog */

/* Configure GPIO pin mode (2 bits per pin in MODER) */
void GPIO_SetMode(GPIO_TypeDef *gpio, uint8_t pin, uint8_t mode) {
    /* Clear 2 bits for this pin */
    gpio->MODER &= ~(0x03 << (pin * 2));
    /* Set new mode */
    gpio->MODER |= (mode << (pin * 2));
}

/* Read GPIO input */
uint8_t GPIO_ReadPin(GPIO_TypeDef *gpio, uint8_t pin) {
    return (gpio->IDR >> pin) & 0x01;
}

/* Write GPIO output */
void GPIO_WritePin(GPIO_TypeDef *gpio, uint8_t pin, uint8_t state) {
    if (state) {
        gpio->BSRR = (1 << pin);         /* Set bit */
    } else {
        gpio->BSRR = (1 << (pin + 16));  /* Reset bit (upper 16 bits) */
    }
}

/* ================================================================
 * PRACTICAL BIT MANIPULATION
 * ================================================================ */

/* Pack two 4-bit values into one byte */
uint8_t pack_nibbles(uint8_t high, uint8_t low) {
    return ((high & 0x0F) << 4) | (low & 0x0F);
}

/* Extract nibbles from byte */
void unpack_nibbles(uint8_t byte, uint8_t *high, uint8_t *low) {
    *high = (byte >> 4) & 0x0F;
    *low  =  byte       & 0x0F;
}

/* Count set bits (popcount) */
uint8_t count_bits(uint32_t val) {
    uint8_t count = 0;
    while (val) {
        count += val & 1;
        val >>= 1;
    }
    return count;
}

/* Check if number is power of 2 */
bool is_power_of_two(uint32_t n) {
    return (n != 0) && ((n & (n - 1)) == 0);
}

/* Reverse bits in a byte */
uint8_t reverse_bits(uint8_t byte) {
    uint8_t result = 0;
    for (int i = 0; i < 8; i++) {
        result = (result << 1) | (byte & 1);
        byte >>= 1;
    }
    return result;
}

/* CRC8 calculation */
uint8_t crc8(const uint8_t *data, uint32_t len) {
    uint8_t crc = 0xFF;
    for (uint32_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x07;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

int main(void) {
    /* Nibble operations */
    uint8_t packed = pack_nibbles(0xA, 0xB);
    printf("Packed: 0x%02X\n", packed);  /* 0xAB */
    
    uint8_t hi, lo;
    unpack_nibbles(0xCD, &hi, &lo);
    printf("Unpacked: 0x%X 0x%X\n", hi, lo);  /* 0xC 0xD */
    
    /* Count bits */
    printf("Bits in 0xFF: %d\n", count_bits(0xFF));    /* 8 */
    printf("Bits in 0xAA: %d\n", count_bits(0xAA));    /* 4 */
    
    /* Power of 2 check */
    printf("Is 16 pow2: %d\n", is_power_of_two(16));  /* 1 */
    printf("Is 15 pow2: %d\n", is_power_of_two(15));  /* 0 */
    
    /* Reverse bits */
    printf("Reverse 0b00000001 = 0b%08d\n", reverse_bits(0x01));  /* 10000000 */
    
    /* CRC8 */
    uint8_t data[] = {0x01, 0x02, 0x03, 0x04};
    printf("CRC8: 0x%02X\n", crc8(data, sizeof(data)));
    
    return 0;
}
```

---

## 15. Advanced Topics

### Recursion and Algorithms

```c
/* advanced.c - Recursion, sorting, searching */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

/* ================================================================
 * SORTING ALGORITHMS
 * ================================================================ */

/* Bubble Sort */
void bubble_sort(int *arr, uint32_t n) {
    for (uint32_t i = 0; i < n - 1; i++) {
        for (uint32_t j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

/* Quick Sort (fastest average case O(n log n)) */
int partition(int *arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;
    
    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            int temp = arr[i]; arr[i] = arr[j]; arr[j] = temp;
        }
    }
    int temp = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = temp;
    return i + 1;
}

void quick_sort(int *arr, int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quick_sort(arr, low, pi - 1);
        quick_sort(arr, pi + 1, high);
    }
}

/* ================================================================
 * SEARCHING ALGORITHMS
 * ================================================================ */

/* Binary Search (array must be sorted!) */
int binary_search(const int *arr, uint32_t n, int target) {
    int low = 0, high = (int)n - 1;
    
    while (low <= high) {
        int mid = low + (high - low) / 2;  /* Avoid overflow */
        
        if (arr[mid] == target) return mid;
        if (arr[mid] < target)  low  = mid + 1;
        else                    high = mid - 1;
    }
    return -1;  /* Not found */
}

/* ================================================================
 * LINKED LIST IMPLEMENTATION
 * ================================================================ */
typedef struct Node {
    int          data;
    struct Node *next;
} Node;

Node* list_create(int data) {
    Node *node = malloc(sizeof(Node));
    if (node == NULL) return NULL;
    node->data = data;
    node->next = NULL;
    return node;
}

void list_append(Node **head, int data) {
    Node *new_node = list_create(data);
    if (new_node == NULL) return;
    
    if (*head == NULL) {
        *head = new_node;
        return;
    }
    
    Node *current = *head;
    while (current->next != NULL) {
        current = current->next;
    }
    current->next = new_node;
}

void list_print(const Node *head) {
    const Node *current = head;
    while (current != NULL) {
        printf("%d -> ", current->data);
        current = current->next;
    }
    printf("NULL\n");
}

void list_free(Node *head) {
    while (head != NULL) {
        Node *next = head->next;
        free(head);
        head = next;
    }
}

int main(void) {
    /* Sorting */
    int arr[] = {64, 34, 25, 12, 22, 11, 90};
    uint32_t n = sizeof(arr) / sizeof(arr[0]);
    
    quick_sort(arr, 0, n - 1);
    printf("Sorted: ");
    for (uint32_t i = 0; i < n; i++) printf("%d ", arr[i]);
    printf("\n");
    
    /* Binary search */
    int idx = binary_search(arr, n, 25);
    printf("Found 25 at index: %d\n", idx);
    
    /* Linked list */
    Node *head = NULL;
    for (int i = 1; i <= 5; i++) {
        list_append(&head, i * 10);
    }
    printf("Linked list: ");
    list_print(head);
    list_free(head);
    head = NULL;
    
    return 0;
}
```

---

## 16. Embedded Systems Patterns

```c
/* embedded_patterns.c - Practical embedded C patterns */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* ================================================================
 * STATE MACHINE PATTERN
 * ================================================================ */
typedef enum {
    STATE_IDLE,
    STATE_INIT,
    STATE_RUNNING,
    STATE_ERROR,
    STATE_SLEEP
} DeviceState;

typedef enum {
    EVENT_START,
    EVENT_STOP,
    EVENT_ERROR,
    EVENT_SLEEP,
    EVENT_WAKE
} DeviceEvent;

/* State transition table */
typedef struct {
    DeviceState  current_state;
    DeviceEvent  event;
    DeviceState  next_state;
    void       (*action)(void);
} Transition;

void action_init(void)    { printf("  Action: Initializing...\n"); }
void action_start(void)   { printf("  Action: Starting device\n"); }
void action_stop(void)    { printf("  Action: Stopping device\n"); }
void action_sleep(void)   { printf("  Action: Going to sleep\n"); }
void action_error(void)   { printf("  Action: Handling error!\n"); }

static const Transition transitions[] = {
    {STATE_IDLE,    EVENT_START, STATE_INIT,    action_init},
    {STATE_INIT,    EVENT_START, STATE_RUNNING, action_start},
    {STATE_RUNNING, EVENT_STOP,  STATE_IDLE,    action_stop},
    {STATE_RUNNING, EVENT_ERROR, STATE_ERROR,   action_error},
    {STATE_RUNNING, EVENT_SLEEP, STATE_SLEEP,   action_sleep},
    {STATE_ERROR,   EVENT_STOP,  STATE_IDLE,    action_stop},
    {STATE_SLEEP,   EVENT_WAKE,  STATE_RUNNING, action_start},
};

DeviceState process_event(DeviceState state, DeviceEvent event) {
    uint32_t n = sizeof(transitions) / sizeof(transitions[0]);
    for (uint32_t i = 0; i < n; i++) {
        if (transitions[i].current_state == state &&
            transitions[i].event == event) {
            if (transitions[i].action != NULL) {
                transitions[i].action();
            }
            return transitions[i].next_state;
        }
    }
    printf("  Invalid transition!\n");
    return state;  /* Stay in current state */
}

/* ================================================================
 * RING BUFFER (UART RX buffer pattern)
 * ================================================================ */
#define RING_BUF_SIZE  16

typedef struct {
    uint8_t  buf[RING_BUF_SIZE];
    uint16_t head;
    uint16_t tail;
    uint16_t count;
} RingBuffer;

void     ring_init(RingBuffer *rb)                          { memset(rb, 0, sizeof(*rb)); }
bool     ring_empty(const RingBuffer *rb)                   { return rb->count == 0; }
bool     ring_full(const RingBuffer *rb)                    { return rb->count == RING_BUF_SIZE; }
uint16_t ring_count(const RingBuffer *rb)                   { return rb->count; }

bool ring_push(RingBuffer *rb, uint8_t data) {
    if (ring_full(rb)) return false;
    rb->buf[rb->head] = data;
    rb->head = (rb->head + 1) % RING_BUF_SIZE;
    rb->count++;
    return true;
}

bool ring_pop(RingBuffer *rb, uint8_t *data) {
    if (ring_empty(rb)) return false;
    *data = rb->buf[rb->tail];
    rb->tail = (rb->tail + 1) % RING_BUF_SIZE;
    rb->count--;
    return true;
}

/* ================================================================
 * COMMAND PARSER PATTERN
 * ================================================================ */
typedef void (*CommandFunc)(const char *args);

typedef struct {
    const char  *name;
    CommandFunc  handler;
    const char  *description;
} Command;

void cmd_help(const char *args)   { printf("Available commands: help, status, reset, led\n"); }
void cmd_status(const char *args) { printf("Device status: OK\n"); }
void cmd_reset(const char *args)  { printf("Resetting device...\n"); }
void cmd_led(const char *args)    { printf("LED: %s\n", args ? args : "toggle"); }

static const Command commands[] = {
    {"help",   cmd_help,   "Show help"},
    {"status", cmd_status, "Show status"},
    {"reset",  cmd_reset,  "Reset device"},
    {"led",    cmd_led,    "Control LED"},
};

void parse_command(char *input) {
    /* Split command and arguments */
    char *cmd  = strtok(input, " ");
    char *args = strtok(NULL, "\0");
    
    if (cmd == NULL) return;
    
    uint32_t n = sizeof(commands) / sizeof(commands[0]);
    for (uint32_t i = 0; i < n; i++) {
        if (strcmp(cmd, commands[i].name) == 0) {
            commands[i].handler(args);
            return;
        }
    }
    printf("Unknown command: %s\n", cmd);
}

int main(void) {
    /* State machine demo */
    printf("=== State Machine ===\n");
    DeviceState state = STATE_IDLE;
    printf("State: IDLE\n");
    
    state = process_event(state, EVENT_START);
    printf("State: INIT\n");
    
    state = process_event(state, EVENT_START);
    printf("State: RUNNING\n");
    
    state = process_event(state, EVENT_SLEEP);
    printf("State: SLEEP\n");
    
    /* Ring buffer demo */
    printf("\n=== Ring Buffer ===\n");
    RingBuffer rb;
    ring_init(&rb);
    
    for (uint8_t i = 0; i < 5; i++) {
        ring_push(&rb, i * 10);
        printf("Pushed: %d\n", i * 10);
    }
    
    printf("Count: %d\n", ring_count(&rb));
    
    uint8_t val;
    while (ring_pop(&rb, &val)) {
        printf("Popped: %d\n", val);
    }
    
    /* Command parser demo */
    printf("\n=== Command Parser ===\n");
    char cmd1[] = "help";
    char cmd2[] = "led on";
    char cmd3[] = "status";
    char cmd4[] = "unknown";
    
    parse_command(cmd1);
    parse_command(cmd2);
    parse_command(cmd3);
    parse_command(cmd4);
    
    return 0;
}
```

---

## 17. Common Mistakes and Best Practices

```c
/* best_practices.c - What to do and what to avoid */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    
    /* ================================================================
     * MISTAKE 1: Integer overflow
     * ================================================================ */
    uint8_t val = 255;
    val++;  /* OVERFLOW! val becomes 0, not 256 */
    printf("Overflow: %d\n", val);  /* 0 */
    
    /* Fix: Check before increment */
    uint8_t safe_val = 255;
    if (safe_val < UINT8_MAX) safe_val++;
    
    /* ================================================================
     * MISTAKE 2: Signed/unsigned comparison
     * ================================================================ */
    int     signed_val   = -1;
    uint32_t unsigned_val = 10;
    
    /* WARNING: -1 as unsigned is huge number! */
    if (signed_val < (int)unsigned_val) {  /* Cast to compare safely */
        printf("signed < unsigned: correct\n");
    }
    
    /* ================================================================
     * MISTAKE 3: Buffer overflow
     * ================================================================ */
    char buf[8];
    /* WRONG: */
    /* strcpy(buf, "This string is too long!");  OVERFLOW! */
    
    /* CORRECT: */
    strncpy(buf, "Hello!!", sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';  /* Always null-terminate */
    
    /* ================================================================
     * MISTAKE 4: Dangling pointer
     * ================================================================ */
    int *ptr = malloc(sizeof(int));
    *ptr = 42;
    free(ptr);
    /* WRONG: ptr still points to freed memory! */
    /* *ptr = 100;  UNDEFINED BEHAVIOR! */
    
    /* CORRECT: Null after free */
    ptr = NULL;
    if (ptr != NULL) {
        *ptr = 100;  /* Safe - never reached */
    }
    
    /* ================================================================
     * MISTAKE 5: Using == for floats
     * ================================================================ */
    float a = 0.1f + 0.2f;
    /* WRONG: */
    /* if (a == 0.3f)  Might be false due to floating point! */
    
    /* CORRECT: Use epsilon comparison */
    #define EPSILON 0.0001f
    if ((a - 0.3f) < EPSILON && (0.3f - a) < EPSILON) {
        printf("Floats are approximately equal\n");
    }
    
    /* ================================================================
     * BEST PRACTICE 1: Always check return values
     * ================================================================ */
    FILE *fp = fopen("test.txt", "r");
    if (fp == NULL) {  /* CHECK! fopen can fail */
        perror("fopen failed");
        /* Handle error gracefully */
    } else {
        fclose(fp);
    }
    
    /* ================================================================
     * BEST PRACTICE 2: Use const for read-only data
     * ================================================================ */
    const uint8_t lookup_table[] = {0, 1, 4, 9, 16, 25};
    /* lookup_table[0] = 99;  ERROR - protected by const */
    
    /* ================================================================
     * BEST PRACTICE 3: Initialize all variables
     * ================================================================ */
    int uninitialized;          /* DANGEROUS - could be anything! */
    int initialized = 0;       /* SAFE */
    char buf2[32];             /* DANGEROUS */
    memset(buf2, 0, sizeof(buf2));  /* SAFE */
    
    /* ================================================================
     * BEST PRACTICE 4: Use typedef for clarity
     * ================================================================ */
    typedef uint32_t Milliseconds;
    typedef uint32_t Hertz;
    
    Milliseconds timeout = 1000;  /* Clear what unit this is */
    Hertz frequency = 100;        /* Clear what unit this is */
    
    printf("Timeout: %u ms\n", timeout);
    printf("Frequency: %u Hz\n", frequency);
    
    return 0;
}
```

---

## Compilation Flags Reference

```bash
# Development build (all warnings, debug info)
gcc -Wall -Wextra -Wpedantic -g -std=c99 file.c -o program

# Release build (optimized, no debug)
gcc -O2 -std=c99 -DNDEBUG file.c -o program

# Embedded build (specific architecture)
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -O2 -std=c99 file.c -o program.elf

# Check for memory errors
gcc -Wall -g -fsanitize=address,undefined file.c -o program

# Static analysis
cppcheck --enable=all file.c

# Check memory leaks
valgrind --leak-check=full ./program

# Common flags explained:
# -Wall        : Enable most warnings
# -Wextra      : Enable extra warnings
# -Wpedantic   : Strict standard compliance
# -g           : Debug symbols
# -O0          : No optimization (default)
# -O1          : Basic optimization
# -O2          : Full optimization
# -O3          : Aggressive optimization
# -Os          : Optimize for size (embedded!)
# -std=c99     : Use C99 standard
# -DDEBUG      : Define DEBUG macro
# -DNDEBUG     : Define NDEBUG (disables assert)
# -I/path      : Add include directory
# -L/path      : Add library directory
# -lm          : Link math library
# -lpthread    : Link pthreads library
```

---

## Quick Reference Card

```c
/* Types */
uint8_t  u8;   uint16_t u16;  uint32_t u32;  uint64_t u64;
int8_t   s8;   int16_t  s16;  int32_t  s32;  int64_t  s64;

/* Control Flow */
if (cond) {}  else if (cond) {}  else {}
for (init; cond; update) {}
while (cond) {}
do {} while (cond);
switch (val) { case X: break; default: break; }

/* Pointers */
int *ptr = &var;  /* Pointer to int */
*ptr = val;       /* Dereference */
ptr->member;      /* Pointer to struct member */
ptr[i];           /* Array indexing */

/* Memory */
void *p = malloc(size);  free(p); p = NULL;
void *p = calloc(n, size);        /* Zero-initialized */
void *p = realloc(p, new_size);   /* Resize */

/* Strings */
strlen(s);    strcpy(dst, src);    strncpy(dst, src, n);
strcmp(a, b); strcat(dst, src);    strncat(dst, src, n);
strchr(s, c); strstr(s, sub);      strtok(s, delim);

/* I/O */
printf("%d %f %s %c %p\n", i, f, s, c, ptr);
scanf("%d %f %s", &i, &f, s);
sprintf(buf, fmt, ...);   snprintf(buf, size, fmt, ...);

/* File */
FILE *fp = fopen(name, "r/w/a/rb/wb");
fgets(buf, size, fp);     fputs(str, fp);
fread(buf, size, n, fp);  fwrite(buf, size, n, fp);
fclose(fp);
```
