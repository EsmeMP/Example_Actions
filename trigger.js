const response = await fetch('https://api.github.com');
const data = await response.json();

console.log(data);
