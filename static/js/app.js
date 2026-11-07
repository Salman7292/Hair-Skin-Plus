// Derma Clinic Management - Vanilla JavaScript Logic

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons if available
    if (window.lucide) {
        lucide.createIcons();
    }

    // --- Search Patient (Client-side fast filter) ---
    const patientSearch = document.getElementById('patient-search');
    if (patientSearch) {
        patientSearch.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const rows = document.querySelectorAll('#patients-table-body tr');
            
            rows.forEach(row => {
                const name = row.getAttribute('data-name').toLowerCase();
                const id = row.getAttribute('data-id').toLowerCase();
                const phone = row.getAttribute('data-phone').toLowerCase();
                
                if (name.includes(query) || id.includes(query) || phone.includes(query)) {
                    row.classList.remove('hidden');
                } else {
                    row.classList.add('hidden');
                }
            });
        });
    }

    // --- Search Medicine in Inventory List (Client-side fast filter) ---
    const medSearch = document.getElementById('medicine-search-inventory');
    if (medSearch) {
        medSearch.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const rows = document.querySelectorAll('#medicines-table-body tr');
            
            rows.forEach(row => {
                const name = row.getAttribute('data-name').toLowerCase();
                const category = row.getAttribute('data-category').toLowerCase();
                
                if (name.includes(query) || category.includes(query)) {
                    row.classList.remove('hidden');
                } else {
                    row.classList.add('hidden');
                }
            });
        });
    }

    // --- Dynamic Prescription Creation Workflow ---
    const prescriptionForm = document.getElementById('prescription-form');
    if (prescriptionForm) {
        let selectedItems = [];

        const medInput = document.getElementById('med_search_input');
        const medDropdown = document.getElementById('med_dropdown');
        const defaultMedsSelect = document.getElementById('default_meds_select');

        const inputMedName = document.getElementById('input_med_name');
        const inputDosage = document.getElementById('input_dosage');
        const inputFrequency = document.getElementById('input_frequency');
        const inputDuration = document.getElementById('input_duration');
        const inputUrdu = document.getElementById('input_urdu');
        const inputMedId = document.getElementById('input_med_id');

        const addMedBtn = document.getElementById('btn_add_medicine');
        const itemsTableBody = document.getElementById('prescription_items_body');
        const medicinesJsonInput = document.getElementById('medicines_json');
        
        // Hide autocomplete dropdown on click outside
        document.addEventListener('click', (e) => {
            if (medDropdown && !medDropdown.contains(e.target) && e.target !== medInput) {
                medDropdown.classList.add('hidden');
            }
        });

        // Autocomplete medicine search
        if (medInput) {
            medInput.addEventListener('input', async (e) => {
                const q = e.target.value.trim();
                if (q.length < 1) {
                    medDropdown.classList.add('hidden');
                    return;
                }

                try {
                    const res = await fetch(`/api/medicines/search?q=${encodeURIComponent(q)}`);
                    const data = await res.json();
                    
                    medDropdown.innerHTML = '';
                    if (data.length > 0) {
                        medDropdown.classList.remove('hidden');
                        data.forEach(med => {
                            const item = document.createElement('div');
                            item.className = 'p-3 hover:bg-slate-100 cursor-pointer border-b border-slate-100 last:border-0 transition duration-150';
                            item.innerHTML = `
                                <div class="font-medium text-slate-800">${med.name}</div>
                                <div class="text-xs text-teal-600 font-semibold">${med.category}</div>
                            `;
                            item.addEventListener('click', () => {
                                selectMedicine(med);
                                medDropdown.classList.add('hidden');
                                medInput.value = '';
                            });
                            medDropdown.appendChild(item);
                        });
                    } else {
                        // Option to add custom typed medicine name
                        medDropdown.classList.remove('hidden');
                        const customItem = document.createElement('div');
                        customItem.className = 'p-3 hover:bg-slate-100 cursor-pointer transition duration-150 text-slate-600 italic text-sm';
                        customItem.innerText = `Add custom medicine: "${q}"`;
                        customItem.addEventListener('click', () => {
                            selectMedicine({
                                id: '',
                                name: q,
                                default_dosage: '',
                                default_frequency: '',
                                default_duration: '',
                                urdu_instructions: ''
                            });
                            medDropdown.classList.add('hidden');
                            medInput.value = '';
                        });
                        medDropdown.appendChild(customItem);
                    }
                } catch (err) {
                    console.error('Error fetching autocomplete:', err);
                }
            });
        }

        // Dropdown selection (Select element trigger)
        if (defaultMedsSelect) {
            defaultMedsSelect.addEventListener('change', async (e) => {
                const medId = e.target.value;
                if (!medId) return;

                try {
                    const res = await fetch(`/api/medicines/search?id=${medId}`);
                    const data = await res.json();
                    if (data && data.length > 0) {
                        selectMedicine(data[0]);
                    }
                } catch (err) {
                    console.error('Error fetching medicine defaults:', err);
                }
                defaultMedsSelect.value = ''; // Reset dropdown
            });
        }

        // Fill inputs with selected medicine data
        function selectMedicine(med) {
            inputMedId.value = med.id || '';
            inputMedName.value = med.name;
            inputDosage.value = med.default_dosage || '';
            inputFrequency.value = med.default_frequency || '';
            inputDuration.value = med.default_duration || '';
            inputUrdu.value = med.urdu_instructions || '';
            inputMedName.focus();
        }

        // Add item to dynamic prescription list
        if (addMedBtn) {
            addMedBtn.addEventListener('click', () => {
                const medName = inputMedName.value.trim();
                const dosage = inputDosage.value.trim();
                const frequency = inputFrequency.value.trim();
                const duration = inputDuration.value.trim();
                const urdu = inputUrdu.value.trim();
                const medId = inputMedId.value;

                if (!medName) {
                    alert('Please enter or select a medicine name.');
                    inputMedName.focus();
                    return;
                }

                // Create item object
                const item = {
                    uniqueId: Date.now(), // Unique key to trace list updates
                    medicine_id: medId ? parseInt(medId) : null,
                    medicine_name: medName,
                    dosage: dosage,
                    frequency: frequency,
                    duration: duration,
                    urdu_instructions: urdu
                };

                selectedItems.push(item);
                renderItems();
                clearInputRow();
            });
        }

        // Clear input boxes after adding to grid
        function clearInputRow() {
            inputMedId.value = '';
            inputMedName.value = '';
            inputDosage.value = '';
            inputFrequency.value = '';
            inputDuration.value = '';
            inputUrdu.value = '';
        }

        // Render selected medicine table
        function renderItems() {
            itemsTableBody.innerHTML = '';
            
            if (selectedItems.length === 0) {
                itemsTableBody.innerHTML = `
                    <tr>
                        <td colspan="5" class="p-6 text-center text-slate-400 italic text-sm">
                            No medicines added yet. Search and add medicines above.
                        </td>
                    </tr>
                `;
                medicinesJsonInput.value = '';
                return;
            }

            selectedItems.forEach((item, index) => {
                const tr = document.createElement('tr');
                tr.className = 'border-b border-slate-100 hover:bg-slate-50 transition duration-150';
                tr.innerHTML = `
                    <td class="p-4">
                        <div class="font-semibold text-slate-800">${item.medicine_name}</div>
                        ${item.urdu_instructions ? `<div class="urdu-text text-sm text-teal-600 mt-1 px-2 py-0.5 bg-teal-50 rounded inline-block" style="line-height:1.6">${item.urdu_instructions}</div>` : ''}
                    </td>
                    <td class="p-4 text-slate-600">${item.dosage || '-'}</td>
                    <td class="p-4 text-slate-600">${item.frequency || '-'}</td>
                    <td class="p-4 text-slate-600">${item.duration || '-'}</td>
                    <td class="p-4 text-center">
                        <div class="flex justify-center space-x-2">
                            <button type="button" class="btn-edit p-1.5 text-blue-600 hover:bg-blue-50 rounded transition duration-150" title="Edit row">
                                <i data-lucide="edit-3" class="w-4 h-4"></i>
                            </button>
                            <button type="button" class="btn-delete p-1.5 text-red-600 hover:bg-red-50 rounded transition duration-150" title="Remove row">
                                <i data-lucide="trash-2" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </td>
                `;

                // Handle edit row action
                tr.querySelector('.btn-edit').addEventListener('click', () => {
                    // Populate inputs
                    inputMedId.value = item.medicine_id || '';
                    inputMedName.value = item.medicine_name;
                    inputDosage.value = item.dosage;
                    inputFrequency.value = item.frequency;
                    inputDuration.value = item.duration;
                    inputUrdu.value = item.urdu_instructions;
                    
                    // Remove from active array and re-render
                    selectedItems.splice(index, 1);
                    renderItems();
                    inputMedName.focus();
                });

                // Handle delete row action
                tr.querySelector('.btn-delete').addEventListener('click', () => {
                    selectedItems.splice(index, 1);
                    renderItems();
                });

                itemsTableBody.appendChild(tr);
            });

            // Update hidden input with latest JSON string
            medicinesJsonInput.value = JSON.stringify(selectedItems);
            
            // Re-render lucide icons inside dynamically added rows
            if (window.lucide) {
                lucide.createIcons();
            }
        }

        // Form Submit Validation
        prescriptionForm.addEventListener('submit', (e) => {
            const diagnosis = document.getElementById('diagnosis').value.trim();
            if (!diagnosis) {
                alert('Please enter a Diagnosis/Skin Condition.');
                e.preventDefault();
                document.getElementById('diagnosis').focus();
                return;
            }

            if (selectedItems.length === 0) {
                alert('Please add at least one medicine to the prescription.');
                e.preventDefault();
                return;
            }
        });
    }

    // --- Delete Confirmations ---
    const deleteForms = document.querySelectorAll('.delete-confirm-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const confirmMsg = form.getAttribute('data-confirm-message') || 'Are you sure you want to delete this record?';
            if (!confirm(confirmMsg)) {
                e.preventDefault();
            }
        });
    });
});
