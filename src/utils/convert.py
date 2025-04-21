from typing import List, Dict


def convert_extract_info_2_html(extracted_list: List[Dict[str, str]]) -> str:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lightcone Comparison</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            pre {
                margin: 0;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            #save-button {
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            #save-button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>Lightcone Comparison</h1>
        <table id="editable-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Input</th>
                    <th>Output</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for run in extracted_list:
        name = run["name"]
        input_json = run["input"]
        output_json = run["output"]
        input_json = run["input"]
        output_json = run["output"]
        # Wrap the JSON in a code block with syntax highlighting
        code_block = f"""
        <tr>
            <td contenteditable="true">{name}</td>
            <td contenteditable="true" spellcheck="false"><pre>{input_json}</pre></td>
            <td contenteditable="true"><pre>{output_json}</pre></td>
        <tr>
        """
        html += code_block
    
    # Add syntax highlighting support
    html += """
            </tbody>
        </table>
        <button id="save-button">Save Changes</button>

    <script>
        // Save button functionality
        const saveButton = document.getElementById('save-button');
        const table = document.getElementById('editable-table');
        const style = document.querySelector('style');

        // Function to save the table content
        const saveChanges = () => {
            const updatedContent = `<style>${style.textContent}</style>${table.outerHTML}`;

            // Send the updated content to the server
            fetch('/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: updatedContent }),
            })
                .then(response => response.json())
                .then(data => {
                    alert('Changes saved successfully!');
                })
                .catch(error => {
                    console.error('Error saving changes:', error);
                    alert('Failed to save changes.');
                });
        };

        // Add event listener to the save button
        saveButton.addEventListener('click', saveChanges);

        // Add keyboard shortcut (Ctrl+S) for saving
        document.addEventListener('keydown', function (event) {
            // Check if Ctrl (or Command on Mac) + S is pressed
            if ((event.ctrlKey || event.metaKey) && event.key === 's') {
                // Prevent the default browser save dialog
                event.preventDefault();

                // Call the save function
                saveChanges();
            }
        });
    </script>
        </body>
    </html>
    """
    return html