
function setVis(element, vis) {
    element.style.visibility = vis ? 'visible' : 'hidden';
}

function toggleVis(name) {
    if (name && (element = document.getElementById(name))) {
	element.classList.toggle('hidden');
    } else {
	console.log('toggleVis("'+name+'"): element not found');
    }
}

/**
 * Set this popover so when it appears, it appears next to this anchor.
 * The anchor can be anything, but typically it's the button that
 * triggered the popover.
 */
function setupPopover(anchor, popover) {
    if (typeof anchor == 'string') anchor = document.getElementById(anchor);
    if (typeof popover == 'string') popover = document.getElementById(popover);

    popover.addEventListener('beforetoggle', (e) => {
        if (e.newState === "open") {
	    const rect = anchor.getBoundingClientRect();
	    const gap = 10; // Space between button and popover
	    popover.style.position = "absolute";
	    popover.style.left = `${rect.right + gap + window.scrollX}px`;
	    popover.style.top = `${rect.top - gap + window.scrollY}px`;
        }
    });
}


// specific to Code Plug O'Rama

/** User clicked on bandFilter checkbox */
function bandFilterVisibility() {
    const form = document.forms["mainForm"];
    const source = form.elements["source"];
    const bandFilter = form.elements["bandFilter"];
    const bandFilterChecks = document.getElementById("bandFilterChecks");
    const checked = bandFilter.checked;
    setVis(bandFilterChecks, checked);
}

/** User clicked on modeFilter checkbox */
function modeFilterVisibility() {
    const form = document.forms["mainForm"];
    const modeFilter = form.elements["modeFilter"];
    const modeFilterChecks = document.getElementById("modeFilterChecks");
    const checked = modeFilter.checked;
    setVis(modeFilterChecks, checked);
}

/** User clicked on input selector */
function inputSelection() {
    const form = document.forms["mainForm"];
    const source = form.elements["source"];
    const selectedValue = source.value
    const dropArea = document.getElementById("drop-area");
    dropArea.hidden = ! selectedValue.startsWith('Upload');
}

function setupDnD() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('fileInput');
    const dropHelp = document.getElementById('drop-help');

    // Prevent defaults for all drag events
    ['dragenter', 'dragover'].forEach(eventName => {
      dropArea.addEventListener(eventName, e => {
	e.preventDefault();
	e.stopPropagation();
	dropArea.classList.add('drag-over');
      }, false);
    });

    // Prevent defaults for all drag events
    ['dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, e => {
	e.preventDefault();
	e.stopPropagation();
	dropArea.classList.remove('drag-over');
      }, false);
    });

    // Handle dropped files
    dropArea.addEventListener('drop', handleFiles);

    // Handle clicks; launch the file chooser
    //console.log("Registering event listener")
    dropArea.addEventListener('click', (e) => {
	//console.log("droparea event: " + e + ", type=" + e.type + ", which=" + e.which + ", detail=" + e.detail);
	e.stopPropagation();
	if (e.target == fileInput) return;	// let fileInput handle it when it arrives
	if (e.target == dropHelp) return;
	fileInput.showPicker();
    });

    //console.log("drag and drop ready to go");
}

/**
 * Handle drag-n-drop. Dropped files are transferred to the
 * fileInput element as if the user had selected them through
 * the picker.
 */
function handleFiles(evt) {
    const files = evt.dataTransfer.files;
    const formData = new FormData();
    const fileInput = document.getElementById('fileInput');

    // Jam these files into the fileInput object
    const dataTransfer = new DataTransfer();
    [...files].forEach(file => {
	dataTransfer.items.add(file);
	//console.log('File moved:', file.name);
    });
    fileInput.files = dataTransfer.files;
    //console.log('Files moved to fileInput')
}
