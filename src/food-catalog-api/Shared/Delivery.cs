namespace FoodApi
{
    public class Delivery(decimal baseRate = 0.2M)
    {
        public decimal getDeliveryCost(decimal Distance) => Distance * baseRate;
    }
}