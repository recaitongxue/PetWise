import{i as t}from"./axios-CXDHTpqi.js";const o={getBreedInfo(e){return t.get(`/breed/${e}`)},submitFeedback(e){return t.post("/feedback",e)},healthCheck(){return t.get("/health_check")}};export{o};
