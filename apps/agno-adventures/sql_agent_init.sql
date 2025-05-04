DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

-- Create departments table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    location VARCHAR(100)
);

-- Create employees table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id), -- Foreign key
    salary INTEGER,
    hire_date DATE
);

-- Insert sample data into departments
INSERT INTO departments (name, location) VALUES
('Engineering', 'Building A'),
('Sales', 'Building B'),
('HR', 'Building A');

-- Insert sample data into employees
INSERT INTO employees (name, department_id, salary, hire_date) VALUES
('Alice Smith', 1, 90000, '2022-01-15'),
('Bob Johnson', 2, 75000, '2021-11-30'),
('Charlie Brown', 1, 95000, '2023-05-01'),
('Diana Ross', 3, 65000, '2022-08-20'),
('Ethan Hunt', 1, 110000, '2020-07-01');

-- Optional: Log completion
\echo 'Database initialized with schema and sample data.'

