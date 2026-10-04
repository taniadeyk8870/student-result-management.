/* ============================================================
   results.js
   Fetches ONE student's result from the backend and renders it.
   The backend's "status" field is the only thing that decides
   PASS vs FAIL - this file never re-computes that decision.
   ============================================================ */

async function loadResult(studentId) {
  const wrapper = document.getElementById("result-wrapper");
  if (!wrapper) return;

  const { ok, data } = await apiRequest(`/api/results/${studentId}`);

  if (!ok) {
    wrapper.innerHTML = `
      <div class="empty-state">
        <i class="bi bi-exclamation-triangle"></i>
        ${escapeHtml(data.error || "Unable to load result")}
      </div>`;
    return;
  }

  if (data.status === "NO_RESULT") {
    wrapper.innerHTML = `
      <div class="empty-state">
        <i class="bi bi-hourglass-split"></i>
        No marks have been recorded for this student yet.
      </div>`;
    return;
  }

  renderResult(data);
}

function renderResult(result) {
  const wrapper = document.getElementById("result-wrapper");

  const subjectRows = result.subjects
    .map(
      (s) => `
      <tr>
        <td>${escapeHtml(s.subject_code)}</td>
        <td>${escapeHtml(s.subject_name)}</td>
        <td>${s.marks}</td>
      </tr>`
    )
    .join("");



  wrapper.innerHTML = `
    <div class="result-card fade-in">
      <div class="result-header">
        <h3 class="mb-0">🎓 STUDENT RESULT MANAGEMENT</h3>
      </div>
      <div class="result-body">
        <div class="result-info-grid">
          <div><div class="label">Student Name</div><div class="value">${escapeHtml(result.name)}</div></div>
          <div><div class="label">Register Number</div><div class="value">${escapeHtml(result.register_number)}</div></div>
          <div><div class="label">Department</div><div class="value">${escapeHtml(result.department)}</div></div>
          <div><div class="label">Semester</div><div class="value">${escapeHtml(result.semester)}</div></div>
        </div>

        <table class="table table-bordered">
          <thead>
            <tr><th>Subject Code</th><th>Subject</th><th>Marks</th></tr>
          </thead>
          <tbody>${subjectRows}</tbody>
        </table>

        <div class="result-summary-grid">
          <div class="result-summary-item"><div class="num">${escapeHtml(result.total)}</div><div class="lbl">Total</div></div>
          <div class="result-summary-item"><div class="num">${escapeHtml(result.average)}</div><div class="lbl">Average</div></div>
          <div class="result-summary-item"><div class="num">${escapeHtml(result.grade)}</div><div class="lbl">Grade</div></div>
          <div class="result-summary-item"><div class="num">${escapeHtml(result.status)}</div><div class="lbl">Status</div></div>
        </div>


        <div class="d-flex gap-2 justify-content-center mt-4 no-print">
          <button class="btn btn-primary-custom" onclick="window.print()"><i class="bi bi-printer"></i> Print Result</button>
          <button class="btn btn-outline-secondary" onclick="downloadResultPdf()"><i class="bi bi-download"></i> Download Result</button>
          <a class="btn btn-outline-dark" href="${window.RESULT_VIEWER === 'admin' ? '/admin/dashboard' : '/student/dashboard'}">
            <i class="bi bi-arrow-left"></i> Back to Dashboard
          </a>
        </div>
      </div>
    </div>`;

  // Backend is the single source of truth: only a PASS status may
  
  
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.RESULT_STUDENT_ID) {
    loadResult(window.RESULT_STUDENT_ID);
  }
});

async function downloadResultPdf(){
  const response=await fetch(`/api/results/${window.RESULT_STUDENT_ID}/pdf`,{credentials:"same-origin"});
  if(!response.ok){let message="Unable to download result";try{const d=await response.json();message=d.error||message;}catch(e){} showAlert("result-wrapper",message);return;}
  const blob=await response.blob();const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="student_result.pdf";document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
}
