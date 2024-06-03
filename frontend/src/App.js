import React, { useState, useEffect } from "react";
import Web3 from "web3";
import ContentRegistry from "./ContentRegistry.json";

const web3 = new Web3(Web3.givenProvider || "http://localhost:8545");
// const contractAddress = "0x03b53E88F320f91a4d1615c21CF21CDE73018429"; // Truffle dağıtımı sonrası alınan contract adresini buraya ekleyin
const contractABI = ContentRegistry.abi;
const networkId = "5777";
const contractAddress = ContentRegistry.networks[networkId]?.address;
const contract = new web3.eth.Contract(contractABI, contractAddress);

function App() {
  const [url, setUrl] = useState("");
  const [txHash, setTxHash] = useState("");
  const [content, setContent] = useState(null);
  const [contentId, setContentId] = useState(null);

  useEffect(() => {
    const checkWeb3 = async () => {
      if (typeof window.ethereum !== "undefined") {
        try {
          await window.ethereum.request({ method: "eth_requestAccounts" });
        } catch (error) {
          console.error("User denied account access");
        }
      } else {
        console.log("No Ethereum browser extension detected");
      }
    };

    checkWeb3();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch("http://localhost:5000/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });
    const data = await response.json();
    setTxHash(data.tx_hash);
    setContentId(data.contentId);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter URL"
        />
        <button type="submit">Submit</button>
      </form>
      {txHash && (
        <div>
          <p>Transaction Hash: {txHash}</p>
          <p>Content ID: {contentId}</p>
        </div>
      )}
    </div>
  );
}

export default App;
