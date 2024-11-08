<script setup>
import { ref } from 'vue'
import {getData, postData} from "@/api/api.js";

const url = ref("")
const selectedReasons = ref([])
const reasons = [
  { value: 1, label: "Наименование закупки совпадает с наименованием в техническом задании и/или в проекте контракта" },
  { value: 2, label: "Обеспечение исполнения контракта - требуется" },
  { value: 3, label: "Наличие сертификатов/лицензий" },
  { value: 4, label: "График поставки И этап поставки" },
  { value: 5, label: "Максимальное значение цены контракта ИЛИ начальная цена" },
  { value: 6, label: "Спецификации" },
]

// Функция для проверки валидности URL
function isValidUrl(string) {
  const pattern = new RegExp('^(https?:\\/\\/)?' +
      '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' +
      '((\\d{1,3}\\.){3}\\d{1,3}))' +
      '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' +
      '(\\?[;&a-z\\d%_.~+=-]*)?' +
      '(\\#[-a-z\\d_]*)?$', 'i');
  return !!pattern.test(string);
}

async function checkKS() {
  const urlsSend = url.value.split('\n').map(item => item.trim()).filter(Boolean);

  if (urlsSend.length === 0) {
    alert("Введите хотя бы один URL для проверки.");
    return;
  }

  const invalidUrls = urlsSend.filter(item => !isValidUrl(item));
  if (invalidUrls.length > 0) {
    alert(`Найдены некорректные URL:\n${invalidUrls.join('\n')}`);
    return;
  }

  if (selectedReasons.value.length === 0) {
    alert("Выберите хотя бы одно основание для проверки.");
    return;
  }
  const selectedLabels = selectedReasons.value
    .map(selected => reasons.find(reason => reason.value === selected)?.label)
    .map((label, index) => `${index + 1}. ${label}`);

  alert(`Проверка КС по URL:\n${urlsSend.join('\n')}\n\nВыбранные основания: \n${selectedLabels.join('\n')}`);

  const response = await postData("analyze", {urls: urlsSend})

}
</script>

<template>
  <div class="container">
    <h2>Основания для снятия КС с публикации</h2>

    <label for="url">Введите URL (каждый с новой строки)</label>
    <textarea id="url" v-model="url" placeholder="Введите URL для проверки, каждый с новой строки..."></textarea>

    <div class="checkbox-group">
      <div v-for="reason in reasons" :key="reason.value" class="checkbox-item">
        <input
            type="checkbox"
            :value="reason.value"
            v-model="selectedReasons"
            :id="'reason-' + reason.value"
        />
        <label :for="'reason-' + reason.value">{{ reason.label }}</label>
      </div>
    </div>

    <button @click="checkKS">Проверить КС</button>
  </div>
</template>

<style scoped>
.container {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #333;
  font-size: 1.5em;
  margin-bottom: 20px;
  text-align: center;
}

label {
  display: block;
  font-size: 1em;
  color: #555;
  margin-bottom: 5px;
}

textarea {
  width: 100%;
  height: 100px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
  resize: vertical;
  margin-bottom: 20px;
  transition: border-color 0.3s;
}

textarea:focus {
  border-color: #007bff;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.checkbox-item {
  display: flex;
  align-items: center;
}

input[type="checkbox"] {
  margin-right: 8px;
}

button {
  display: inline-block;
  width: 100%;
  padding: 10px;
  font-size: 1em;
  color: #fff;
  background-color: #007bff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #0056b3
}

button:active {
  background-color: #003d80;
}
</style>