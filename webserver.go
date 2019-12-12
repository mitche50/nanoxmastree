package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"

	"database/sql"

	"github.com/go-redis/redis"
	_ "github.com/go-sql-driver/mysql"
	"github.com/gorilla/websocket"
	"github.com/joho/godotenv"
)

type donationRecord struct {
	Address string
	Amount  string
}

func init() {
	// loads values from .env into the system
	if err := godotenv.Load(); err != nil {
		log.Print("No .env file found")
	}
}

func sendBalance(c *websocket.Conn, client *redis.Client) {
	// sends the balance to the provided websocket
	balance, _ := client.Get("donations").Result()
	fiat, _ := client.Get("donations-fiat").Result()
	balanceMessage := make(map[string]string)
	balanceMessage["balance"] = balance
	balanceMessage["fiat"] = fiat
	balanceJSON, _ := json.Marshal(balanceMessage)
	err := c.WriteMessage(websocket.TextMessage, []byte(balanceJSON))
	if err != nil {
		log.Print("websocket error:", err)
	}
	return
}

func sendDonations(c *websocket.Conn, db *sql.DB) {
	// sends a list of the top 10 donations
	var (
		account string
		amount  string
	)
	rows, err := db.Query("select address, sum(amount) from xmas.xmas_donations group by address order by sum(amount) DESC limit 10;")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	topDonations := make([]string, 11)
	topDonations[0] = "top"
	sI := 1

	for rows.Next() {
		err := rows.Scan(&account, &amount)
		if err != nil {
			log.Fatal(err)
		}
		topDonations[sI] = fmt.Sprintf("%v,%v", account, amount)
		sI++
	}
	err = rows.Err()
	if err != nil {
		log.Fatal(err)
	}

	topJSON, _ := json.Marshal(topDonations)
	err = c.WriteMessage(websocket.TextMessage, []byte(topJSON))
	if err != nil {
		log.Print("websocket error:", err)
	}
	return
}

func xmas(w http.ResponseWriter, r *http.Request) {
	var upgrader = websocket.Upgrader{} // use default options
	upgrader.CheckOrigin = func(r *http.Request) bool { return true }
	c, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Print("upgrade:", err)
		return
	}
	defer c.Close()

	redisHost, exists := os.LookupEnv("REDIS_HOST")
	if !exists {
		redisHost = "localhost"
	}
	redisPort, exists := os.LookupEnv("REDIS_PORT")
	if !exists {
		redisPort = "6379"
	}
	redisPW, exists := os.LookupEnv("REDIS_PW")
	if !exists {
		redisPW = ""
	}
	mySQLHost, exists := os.LookupEnv("MYSQL_HOST")
	if !exists {
		mySQLHost = "localhost"
	}
	mySQLUser, exists := os.LookupEnv("MYSQL_USER")
	if !exists {
		mySQLUser = "test"
	}
	mySQLPW, exists := os.LookupEnv("MYSQL_PW")
	if !exists {
		mySQLPW = ""
	}
	mySQLDB, exists := os.LookupEnv("MYSQL_DB")
	if !exists {
		mySQLDB = "xmas"
	}

	db, err := sql.Open("mysql", fmt.Sprintf("%v:%v@tcp(%v:3306)/%v", mySQLUser, mySQLPW, mySQLHost, mySQLDB))
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	fmt.Println(fmt.Sprintf("%v:%v", redisHost, redisPort))

	client := redis.NewClient(&redis.Options{
		Addr:     fmt.Sprintf("%v:%v", redisHost, redisPort),
		Password: redisPW, // no password set
		DB:       0,       // use default DB
	})
	defer client.Close()

	go func() {
		p := client.Subscribe("PendingAnimations", "AnimationProcessing", "AnimationCompleted", "test")
		fmt.Println("in goroutine")
		for {
			msg, err := p.ReceiveMessage()
			if err != nil {
				break
			}

			fmt.Println(msg.Channel, msg.Payload)
			switch msg.Channel {
			case "AnimationProcessing":
				fmt.Println(msg.Channel, msg.Payload)
				wsData, _ := json.Marshal(msg.Payload)
				sendBalance(c, client)
				sendDonations(c, db)
				err = c.WriteMessage(websocket.TextMessage, wsData)
			case "PendingAnimations":
				err = c.WriteMessage(websocket.TextMessage, []byte(msg.Payload))
			case "AnimationCompleted":
				err = c.WriteMessage(websocket.TextMessage, []byte("done"))
			case "test":
				sendDonations(c, db)
			}
		}
	}()

	rData, err := client.LRange("animations", 0, 9).Result()
	if err != nil {
		panic(err)
	}
	print(rData)

	testJSON, _ := json.Marshal(rData)

	err = c.WriteMessage(websocket.TextMessage, testJSON)
	sendBalance(c, client)
	sendDonations(c, db)

	for {
		_, message, err := c.ReadMessage()
		if err != nil {
			log.Println("read:", err)
			break
		}
		log.Printf("recv: %s", message)
	}
}

func main() {

	var addr = flag.String("addr", "localhost:2512", "http service address")

	flag.Parse()
	log.SetFlags(0)

	http.HandleFunc("/", xmas)
	log.Fatal(http.ListenAndServe(*addr, nil))
}
