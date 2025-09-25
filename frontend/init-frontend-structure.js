// init-frontend-structure.js
// Run: node init-frontend-structure.js
// Make sure you are in your frontend folder

const fs = require("fs");
const path = require("path");

const structure = {
  src: {
    api: ["api.ts"],
    components: {
      charts: ["LineChart.tsx"],
      layout: ["Header.tsx", "Sidebar.tsx"],
      common: ["Button.tsx"]
    },
    pages: ["Home.tsx", "Admin.tsx", "Login.tsx"],
    types: ["index.ts"],
    "App.tsx": "",
    "index.tsx": ""
  },
  public: {}
};

function createStructure(basePath, obj) {
  for (const key in obj) {
    const currentPath = path.join(basePath, key);
    if (Array.isArray(obj[key])) {
      // key is a folder, value is list of files
      fs.mkdirSync(currentPath, { recursive: true });
      obj[key].forEach(file => {
        fs.writeFileSync(path.join(currentPath, file), "");
      });
    } else if (typeof obj[key] === "object") {
      fs.mkdirSync(currentPath, { recursive: true });
      createStructure(currentPath, obj[key]);
    } else {
      // key is a file
      fs.writeFileSync(currentPath, "");
    }
  }
}

createStructure(process.cwd(), structure);

console.log("Frontend folder structure created successfully!");
