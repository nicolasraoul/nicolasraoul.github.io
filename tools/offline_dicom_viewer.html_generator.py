import os

# Read the dicom parser code
with open('dicomParser.js', 'r') as f:
    dicom_parser_code = f.read()

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Offline DICOM Viewer & Extractor</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f5f5f7;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{ text-align: center; color: #111; }}
        .info-section {{
            background: #fff;
            padding: 20px 30px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            line-height: 1.5;
        }}
        .info-section h2 {{ margin-top: 0; color: #007bff; font-size: 1.3em; }}
        .info-section h3 {{ margin-top: 15px; margin-bottom: 5px; color: #333; font-size: 1.1em; }}
        .info-section ul {{ margin-bottom: 0; padding-left: 20px; }}
        .drop-zone {{
            display: block;
            border: 3px dashed #007bff;
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
            background: #fff;
            font-size: 1.2em;
            color: #555;
            cursor: pointer;
            transition: background 0.2s, border-color 0.2s;
            margin-bottom: 20px;
        }}
        .drop-zone.dragover {{ background: #e9f5ff; border-color: #0056b3; }}
        #status {{ text-align: center; font-weight: bold; margin-bottom: 20px; color: #0056b3; }}
        .gallery {{ display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }}
        .card {{
            background: #fff;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 300px;
        }}
        canvas {{ max-width: 100%; border-radius: 4px; background: #000; margin-bottom: 15px; }}
        .filename {{ word-break: break-all; font-size: 0.9em; margin-bottom: 10px; color: #666; text-align: center; }}
        button {{
            background: #007bff; color: white; border: none; padding: 10px 20px;
            border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.2s;
            width: 100%;
        }}
        button:hover {{ background: #0056b3; }}
        .download-all {{ margin-bottom: 20px; text-align: center; display: none; }}
    </style>
    <script>
        // --- DICOM PARSER START ---
        {dicom_parser_code}
        // --- DICOM PARSER END ---
    </script>
</head>
<body>

    <h1>Offline DICOM Viewer & Extractor</h1>
    
    <div class="info-section">
        <h2>About This Tool</h2>
        <p>If you have received a medical CD/DVD (such as a Portable Data for Imaging or PDI disk) and are wondering how to view its contents—especially if you use a Mac, Linux, or a modern Windows PC where the included outdated viewer doesn't work—this tool is for you.</p>
        <p>Medical images on these disks are usually stored in <strong>DICOM</strong> format, inside a "DICOM" folder, without standard file extensions like .jpg. This viewer seamlessly extracts those images so you can save them normally.</p>
        
        <h3>How to Use</h3>
        <ul>
            <li><strong>Drag and Drop:</strong> Simply drag the entire "DICOM" folder from your CD/DVD directly into the dashed blue box below.</li>
            <li><strong>Click to Select:</strong> Alternatively, click the dashed box to manually select the DICOM folder from your computer.</li>
            <li><strong>Download:</strong> Once the X-rays or scans appear, you can save them individually or click "Download All as JPG" to save them all at once.</li>
        </ul>

        <h3>🔒 Privacy & Security</h3>
        <p><strong>100% Offline & Private:</strong> This web page is completely self-contained. It processes all medical images entirely on your own machine. <strong>No data, images, or personal information is ever uploaded or sent over the internet.</strong> You can completely disconnect your computer from Wi-Fi immediately after opening this file and it will still work perfectly.</p>
    </div>

    <label class="drop-zone" id="dropArea" for="fileInput">
        Drop your "DICOM" folder here (or click to select folder)
        <input type="file" id="fileInput" webkitdirectory directory multiple style="position: absolute; width: 0; height: 0; overflow: hidden; opacity: 0;">
    </label>

    <div id="status"></div>
    <div class="download-all" id="downloadAllContainer">
        <button id="downloadAllBtn" style="width: auto;">Download All as JPG</button>
    </div>
    
    <div class="gallery" id="gallery"></div>

    <footer style="margin-top: 40px; text-align: center; color: #777; font-size: 0.9em; padding-bottom: 20px;">
        Powered by the open-source <a href="https://github.com/cornerstonejs/dicomParser" target="_blank" style="color: #007bff; text-decoration: none;">dicomParser</a> library. Thank you to the cornerstonejs contributors!
    </footer>

    <script>
        const dropArea = document.getElementById('dropArea');
        const fileInput = document.getElementById('fileInput');
        const statusEl = document.getElementById('status');
        const gallery = document.getElementById('gallery');
        const downloadAllContainer = document.getElementById('downloadAllContainer');
        const downloadAllBtn = document.getElementById('downloadAllBtn');
        
        let processedImages = [];

        // Prevent default browser behavior for drag and drop globally
        window.addEventListener('dragover', e => e.preventDefault());
        window.addEventListener('drop', e => e.preventDefault());

        dropArea.addEventListener('dragover', (e) => {{ e.preventDefault(); e.stopPropagation(); dropArea.classList.add('dragover'); }});
        dropArea.addEventListener('dragleave', (e) => {{ e.preventDefault(); e.stopPropagation(); dropArea.classList.remove('dragover'); }});
        dropArea.addEventListener('drop', async (e) => {{
            e.preventDefault();
            e.stopPropagation();
            dropArea.classList.remove('dragover');
            
            statusEl.innerText = 'Extracting files from folder...';
            const files = [];
            
            if (e.dataTransfer.items) {{
                const promises = [];
                for (let i = 0; i < e.dataTransfer.items.length; i++) {{
                    const item = e.dataTransfer.items[i];
                    if (item.kind === 'file') {{
                        const entry = item.webkitGetAsEntry();
                        if (entry) {{
                            promises.push(traverseFileTree(entry, '', files));
                        }}
                    }}
                }}
                await Promise.all(promises);
            }} else {{
                for (let i = 0; i < e.dataTransfer.files.length; i++) {{
                    files.push(e.dataTransfer.files[i]);
                }}
            }}
            handleFiles(files);
        }});
        
        fileInput.addEventListener('change', (e) => handleFiles(Array.from(e.target.files)));

        async function traverseFileTree(item, path, filesArray) {{
            if (item.isFile) {{
                return new Promise((resolve) => {{
                    item.file(file => {{
                        file.fullPath = path + file.name;
                        filesArray.push(file);
                        resolve();
                    }});
                }});
            }} else if (item.isDirectory) {{
                const dirReader = item.createReader();
                const entries = await readAllDirectoryEntries(dirReader);
                const promises = entries.map(entry => traverseFileTree(entry, path + item.name + "/", filesArray));
                await Promise.all(promises);
            }}
        }}

        function readAllDirectoryEntries(dirReader) {{
            return new Promise((resolve, reject) => {{
                let allEntries = [];
                function readEntries() {{
                    dirReader.readEntries((entries) => {{
                        if (entries.length === 0) {{
                            resolve(allEntries);
                        }} else {{
                            allEntries = allEntries.concat(entries);
                            readEntries();
                        }}
                    }}, reject);
                }}
                readEntries();
            }});
        }}

        async function handleFiles(files) {{
            gallery.innerHTML = '';
            statusEl.innerText = 'Processing files...';
            processedImages = [];
            downloadAllContainer.style.display = 'none';
            
            let count = 0;
            let success = 0;
            
            for (let i = 0; i < files.length; i++) {{
                const file = files[i];
                // Skip hidden files and non-dicom standard files like DICOMDIR
                if (file.name.startsWith('.') || file.name === 'DICOMDIR' || file.name === 'README.TXT') continue;
                
                count++;
                try {{
                    const arrayBuffer = await file.arrayBuffer();
                    const byteArray = new Uint8Array(arrayBuffer);
                    
                    let dataSet;
                    try {{
                        dataSet = dicomParser.parseDicom(byteArray);
                    }} catch (err) {{ continue; }} // Not a valid dicom
                    
                    const renderedResult = renderDicomToCanvas(dataSet, byteArray);
                    if (renderedResult) {{
                        const {{ canvas, width, height }} = renderedResult;
                        
                        const card = document.createElement('div');
                        card.className = 'card';
                        
                        const fname = document.createElement('div');
                        fname.className = 'filename';
                        fname.innerText = file.webkitRelativePath || file.name;
                        
                        const btn = document.createElement('button');
                        btn.innerText = 'Download JPG';
                        
                        btn.onclick = () => {{
                            const link = document.createElement('a');
                            link.download = (file.name || 'image') + '.jpg';
                            link.href = canvas.toDataURL('image/jpeg', 0.95);
                            link.click();
                        }};
                        
                        processedImages.push({{
                            canvas: canvas,
                            name: (file.name || 'image') + '.jpg'
                        }});
                        
                        card.appendChild(canvas);
                        card.appendChild(fname);
                        card.appendChild(btn);
                        gallery.appendChild(card);
                        success++;
                    }}
                }} catch (e) {{
                    console.warn('Error processing', file.name, e);
                }}
            }}
            
            statusEl.innerText = `Found ${{success}} usable images out of ${{count}} files inspected.`;
            if (success > 0) {{
                downloadAllContainer.style.display = 'block';
            }}
        }}
        
        // Single file force download
        downloadAllBtn.addEventListener('click', () => {{
            processedImages.forEach((img, idx) => {{
                setTimeout(() => {{
                    const link = document.createElement('a');
                    link.download = img.name;
                    link.href = img.canvas.toDataURL('image/jpeg', 0.95);
                    link.click();
                }}, idx * 300); // Stagger downloads
            }});
        }});

        function renderDicomToCanvas(dataSet, byteArray) {{
            // We need 7fe0,0010 for Pixel Data
            const pixelDataElement = dataSet.elements.x7fe00010;
            if (!pixelDataElement) return null;

            const rows = dataSet.uint16('x00280010');
            const cols = dataSet.uint16('x00280011');
            const bitsAllocated = dataSet.uint16('x00280100');
            const pixelRepresentation = dataSet.uint16('x00280103'); // 0=unsigned, 1=signed
            const samplesPerPixel = dataSet.uint16('x00280002');
            
            // Getting rescale and window settings safely
            const getStr = (tag) => {{
                let val = dataSet.string(tag);
                if (val && val.includes('\\\\')) val = val.split('\\\\')[0];
                return val ? parseFloat(val) : 0;
            }};
            
            let rescaleIntercept = getStr('x00281052') || 0;
            let rescaleSlope = getStr('x00281053') || 1;
            let windowCenter = getStr('x00281050');
            let windowWidth = getStr('x00281051');

            const length = pixelDataElement.length;
            const offset = pixelDataElement.dataOffset;
            const pixelBuffer = byteArray.buffer.slice(offset, offset + length);
            
            let pixelValues;
            if (bitsAllocated === 8) {{
                pixelValues = new Uint8Array(pixelBuffer);
            }} else if (bitsAllocated === 16) {{
                pixelValues = pixelRepresentation === 1 ? new Int16Array(pixelBuffer) : new Uint16Array(pixelBuffer);
            }} else {{
                return null; // Unsupported depth
            }}

            // If no window center/width provided, calculate from min/max
            if (!windowCenter || !windowWidth) {{
                let min = Infinity;
                let max = -Infinity;
                for (let i = 0; i < pixelValues.length; i++) {{
                    let val = pixelValues[i] * rescaleSlope + rescaleIntercept;
                    if (val < min) min = val;
                    if (val > max) max = val;
                }}
                windowWidth = max - min;
                windowCenter = min + windowWidth / 2;
            }}

            const canvas = document.createElement('canvas');
            canvas.width = cols;
            canvas.height = rows;
            const ctx = canvas.getContext('2d');
            const imageData = ctx.createImageData(cols, rows);
            const data = imageData.data;

            const minWindow = windowCenter - 0.5 - (windowWidth - 1) / 2;
            const maxWindow = windowCenter - 0.5 + (windowWidth - 1) / 2;

            if (samplesPerPixel === 1) {{
                for (let i = 0; i < pixelValues.length; i++) {{
                    let val = pixelValues[i] * rescaleSlope + rescaleIntercept;
                    
                    let mapped = 0;
                    if (val <= minWindow) {{
                        mapped = 0;
                    }} else if (val > maxWindow) {{
                        mapped = 255;
                    }} else {{
                        mapped = Math.round(((val - windowCenter) / windowWidth + 0.5) * 255.0);
                    }}
                    
                    const idx = i * 4;
                    data[idx] = mapped;
                    data[idx+1] = mapped;
                    data[idx+2] = mapped;
                    data[idx+3] = 255;
                }}
            }} else if (samplesPerPixel === 3) {{
                // RGB logic (rare for standard raw, but just in case)
                for (let i = 0; i < pixelValues.length / 3; i++) {{
                    const idx = i * 4;
                    const vIdx = i * 3;
                    data[idx] = pixelValues[vIdx];
                    data[idx+1] = pixelValues[vIdx+1];
                    data[idx+2] = pixelValues[vIdx+2];
                    data[idx+3] = 255;
                }}
            }}

            ctx.putImageData(imageData, 0, 0);
            return {{ canvas, width: cols, height: rows }};
        }}
    </script>
</body>
</html>
"""

with open('offline_dicom_viewer.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("Generated offline_dicom_viewer.html")
