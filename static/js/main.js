/* Shared helpers and authentication logic. */
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function showAlert(containerId, message, type = "danger") {
  const container=document.getElementById(containerId); if(!container)return;
  container.innerHTML=`<div class="alert alert-${escapeHtml(type)} alert-dismissible fade show" role="alert">${escapeHtml(message)}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`;
}
async function apiRequest(url,method="GET",body=null){
  const options={method,headers:{"Content-Type":"application/json"},credentials:"same-origin"};
  if(body!==null)options.body=JSON.stringify(body);
  const response=await fetch(url,options);let data={};try{data=await response.json();}catch(e){}
  return {ok:response.ok,status:response.status,data};
}
document.addEventListener("DOMContentLoaded",()=>{
  const adminForm=document.getElementById("admin-login-form");
  adminForm?.addEventListener("submit",async e=>{e.preventDefault();const username=document.getElementById("admin-username").value.trim(),password=document.getElementById("admin-password").value;const r=await apiRequest("/api/admin/login","POST",{username,password});if(r.ok)location.href="/admin/dashboard";else showAlert("admin-login-alert",r.data.error||"Invalid username or password");});
  const studentForm=document.getElementById("student-login-form");
  studentForm?.addEventListener("submit",async e=>{e.preventDefault();const register_number=document.getElementById("student-register-number").value.trim(),password=document.getElementById("student-password").value;const r=await apiRequest("/api/student/login","POST",{register_number,password});if(r.ok)location.href="/student/dashboard";else showAlert("student-login-alert",r.data.error||"Invalid register number or password");});
  document.querySelectorAll(".logout-btn").forEach(btn=>btn.addEventListener("click",async e=>{e.preventDefault();await apiRequest("/api/logout","POST");location.href="/";}));
  const toggle=document.querySelector(".sidebar-toggle-btn"),sidebar=document.querySelector(".sidebar");toggle?.addEventListener("click",()=>sidebar?.classList.toggle("show"));
});
