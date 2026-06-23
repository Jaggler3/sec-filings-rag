package main

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

type QueryParams struct {
	Text string `json:"text"`
}

func main() {
	router := gin.Default()

	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:5173"},
		AllowMethods:     []string{"GET", "POST"},
		AllowHeaders:     []string{"Content-Type", "Content-Length", "Accept-Encoding", "X-CSRF-Token", "Authorization", "accept", "origin", "Cache-Control", "X-Requested-With"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "OK",
		})
	})

	router.POST("/query", func(c *gin.Context) {
		// get query body data
		var body QueryParams
		if err := c.ShouldBindJSON(&body); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// make json for proxy request
		data := map[string]string{
			"text": body.Text,
		}
		jsonData, err := json.Marshal(data)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "could not form payload"})
			return
		}

		// send request to python
		response, err := http.Post("http://localhost:8000/query", "application/json", bytes.NewBuffer(jsonData))
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "could not get response from python"})
			return
		}
		defer response.Body.Close()

		responseBody, err := io.ReadAll(response.Body)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "could not read response body from python"})
			return
		}

		// unmarshall it
		var result any
		if err := json.Unmarshal(responseBody, &result); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "invalid JSON from python"})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"response": result,
		})
	})
	router.Run(":7070")
}
