# Webcam Processor and Reader

This project consists of two parts: a Python-based webcam processor and a Next.js-based webcam reader. The webcam processor captures and processes webcam data, which is then displayed by the webcam reader.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Running the Webcam Processor](#running-the-webcam-processor)
  - [Running the Webcam Reader](#running-the-webcam-reader)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Python 3.7+
- Node.js 14+
- npm or yarn

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/webcam-processor-reader.git
   ```

2. Set up the Python environment:

   ```bash
   cd webcam-processor
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Set up the Next.js project:

   ```bash
   cd webcam-reader
   npm install
   # or
   yarn install
   ```

## Usage

### Running the Webcam Processor

1. Activate the Python virtual environment (if not already activated):

   ```bash
   cd webcam-processor
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

2. Run the webcam processor:

   ```bash
   python3 src/proc.py
   ```

### Running the Webcam Reader

1. In a new terminal, navigate to the webcam-reader directory:

   ```bash
   cd webcam-reader
   ```

2. Start the Next.js development server:

   ```bash
   npm run dev
   # or
   yarn dev
   ```

3. Open your browser and go to `http://localhost:3000`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.