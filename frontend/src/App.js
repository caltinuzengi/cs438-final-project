import React, { useState, useEffect } from "react";
import Web3 from "web3";
import ContentRegistry from "./ContentRegistry.json";

import { Container, Form, Button, Card, ListGroup, Alert } from 'react-bootstrap';
import './App.css'; 


const web3 = new Web3(Web3.givenProvider || "http://localhost:8545");
// const contractAddress = "0x03b53E88F320f91a4d1615c21CF21CDE73018429"; // Truffle dağıtımı sonrası alınan contract adresini buraya ekleyin
const contractABI = ContentRegistry.abi;
const networkId = "5777";
const contractAddress = ContentRegistry.networks[networkId]?.address;
const contract = new web3.eth.Contract(contractABI, contractAddress);

function App() {
  const [url, setUrl] = useState("");
  const [txHash, setTxHash] = useState("");
  const [contents, setContents] = useState([]);
  // const [content, setContent] = useState(null);
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

    const fetchContents = async () => {
      const response = await fetch("http://localhost:5000/contents");
      const data = await response.json();
      setContents(data.reverse());
    };    

    checkWeb3();
    fetchContents();
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
    fetchContents();
  };

  const fetchContents = async () => {
    const response = await fetch("http://localhost:5000/contents");
    const data = await response.json();
    setContents(data.reverse());
  };

  return (
    <Container>
      <header className="app-header">
        <h1 className="title">News Scribe</h1>
      </header>
      <Form onSubmit={handleSubmit} className="mt-3">
        <Form.Group controlId="formUrl">
          <Form.Label>Enter URL</Form.Label>
          <Form.Control
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter URL"
          />
        </Form.Group>
        <Button variant="primary" type="submit" className="mt-3">
          Submit
        </Button>
      </Form>
      {txHash && (
        <Alert variant="success" className="mt-3">
          Last Submitted Transaction Hash: {txHash}
        </Alert>
      )}
      <h3 className="mt-5">Submitted Contents</h3>
      <ListGroup className="mt-3">
        {contents.map(content => (
          <ListGroup.Item key={content.id}>
            <Card>
              <Card.Body>
                <Card.Title>{content.title}</Card.Title>
                <Card.Text>{content.content}</Card.Text>
                <Card.Text><strong>Author:</strong> {content.author}</Card.Text>
                <Card.Text><strong>Date:</strong> {content.date}</Card.Text>
                <Card.Text><strong>Transaction Hash:</strong> {content.tx_hash}</Card.Text>
              </Card.Body>
            </Card>
          </ListGroup.Item>
        ))}
      </ListGroup>
    </Container>
  );
}

export default App;
