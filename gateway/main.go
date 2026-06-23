package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type QueryParams struct {
	Text string `json:"text"`
}

func main() {
	r := gin.Default()

	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "OK",
		})
	})

	r.POST("/query", func(c *gin.Context) {
		var body QueryParams
		if err := c.ShouldBindJSON(&body); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"response": "your query was: '" + body.Text + "'",
		})
	})

	r.Run(":7070")
}
