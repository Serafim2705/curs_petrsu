var doc_btn_ids = ["btn_report", "btn_missing_report", "btn_directive_bak", "btn_directive_mag"];
/*  function search(a) {
    var b = $("input[type\x3dsubmit][clicked\x3dtrue]").attr("id");

    -1 === doc_btn_ids.indexOf(b) && (a.preventDefault(),
   jQuery.ajax({
        url: "/",
        type: "POST",
        dataType: "html",
        data: jQuery("#webd_form").serialize(),
        success: function(a) {
            // document.getElementById("webd_result").innerHTML = a
            //document.getElementById("webd_result").innerHTML = a
            // $('webd_result').html(a)
            document.getElementById("webd_result").html = a
        },
        error: function(a) {
             document.getElementById("webd_result").innerHTML = "Ошибка в запросе"
        }
    }),
    a.preventDefault())
    
} */
// Сохранение содержимого полей HTML в sessionStorage
function saveFields() {
    var fieldsToSave = ['inp_year', 'inp_group', 'inp_department','inp_student','inp_adviser','group_method','sort_method','sort_order']; // Здесь перечислите идентификаторы полей, которые вы хотите сохранить
  
    fieldsToSave.forEach(function(fieldId) {
      var field = document.getElementById(fieldId);
      if (field) {
        sessionStorage.setItem(fieldId, field.value);
      }
    });
  }
  
  // Восстановление содержимого полей HTML из sessionStorage
  function restoreFields() {
    var fieldsToRestore = ['inp_year', 'inp_group', 'inp_department','inp_student','inp_adviser','group_method','sort_method','sort_order']; // Здесь перечислите идентификаторы полей, которые вы хотите восстановить
  
    fieldsToRestore.forEach(function(fieldId) {
      var field = document.getElementById(fieldId);
      if (field && sessionStorage.getItem(fieldId)) {
        field.value = sessionStorage.getItem(fieldId);
      }
    });
  }


  document.addEventListener('DOMContentLoaded', function() {
    restoreFields();
  });




function validate_file(a) {
    10485760 < a.files[0].size ? ($("#result_" + a.id + "_failure").text("Файлы размером более 10мб недопустимы!"),
    $("#submit_" + a.id).attr("disabled", "disabled"),
    $("#result_" + a.id + "_success").text("")) : "application/pdf" != a.files[0].type ? ($("#result_" + a.id + "_failure").text("Допустимы файлы только формата PDF!"),
    $("#result_" + a.id + "_success").text(""),
    $("#submit_" + a.id).attr("disabled", "disabled")) : ($("#result_" + a.id + "_failure").text(""),
    $("#result_" + a.id + "_success").text(""),
    $("#submit_" + a.id).removeAttr("disabled"));
    $("#" + a.id).removeAttr("style")
}
function showHideAdditional() {
    var a = document.getElementById("webd_form_additional").classList;
    a.toggle("hidden");
    document.getElementById("webd_form_show_additional").innerHTML = a.contains("hidden") ? "Больше \x26darr;" : "Меньше \x26uarr;";
    document.getElementById("btn_missing_report").classList.toggle("hidden")
}
function togglePrvYearInstruction() {
    var a = document.getElementById("prv_year_instruction_content").classList;
    a.toggle("hidden");
    document.getElementById("prv_year_instruction_button").innerHTML = a.contains("hidden") ? "Инструкция по редактированию прошлых лет \x26darr;" : "Инструкция по редактированию прошлых лет \x26uarr;"
}
$(document).ready(function() {
    $("#js_check").remove();
    $("form input[type\x3dsubmit]").click(function() {
        $("input[type\x3dsubmit]", $(this).parents("form")).removeAttr("clicked");
        $(this).attr("clicked", "true")
    });
    $("#webd_form").submit(search)
});