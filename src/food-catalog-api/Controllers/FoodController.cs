using System.Collections.Generic;
using System.Linq;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System;
using Microsoft.Identity.Web.Resource;
using Microsoft.Extensions.Configuration;
using FoodApp;

namespace FoodApi
{
    [Route("[controller]")]
    [ApiController]
    public class FoodController(FoodDBContext Ctx, IConfiguration config) : ControllerBase
    {
        private FoodConfig Cfg { get; } = config.Get<FoodConfig>();

        // http://localhost:PORT/food
        [HttpGet()]
        public IEnumerable<FoodItem> GetFood()
        {
            return Ctx.Food.ToArray();
        }

        // GET /food/byname?name=Apple
        [HttpGet("byname")]
        public ActionResult<IEnumerable<FoodItem>> GetFoodByName([FromQuery] string name)
        {
            if (string.IsNullOrWhiteSpace(name))
                return BadRequest("Name parameter is required.");
            var items = Ctx.Food.Where(f => f.Name.Contains(name)).ToList();
            if (items.Count == 0)
                return NotFound();
            return Ok(items);
        }

        // http://localhost:PORT/food/3
        [HttpGet("{id}")]
        public FoodItem GetById(int id)
        {
            return Ctx.Food.FirstOrDefault(v => v.ID == id);
        }

        // http://localhost:PORT/food
        [HttpPost()]
        public FoodItem InsertFood(FoodItem item)
        {
            Ctx.Food.Add(item);
            Ctx.SaveChanges();

            if (Cfg.FeatureManagement.PublishEvents)
            {
                Console.WriteLine("Publishing event to Service Bus - mock");
            }
            return item;
        }

        // http://localhost:PORT/food
        [HttpPut()]
        public FoodItem UpdateFood(FoodItem item)
        {
            Ctx.Food.Attach(item);
            Ctx.Entry(item).State = EntityState.Modified;
            Ctx.SaveChanges();

            if (Cfg.FeatureManagement.PublishEvents)
            {
                Console.WriteLine("Publishing event to Service Bus - mock");
            }
            return item;
        }

        // http://localhost:PORT/food
        [HttpDelete("{id}")]
        public ActionResult Delete(int id)
        {
            var item = GetById(id);
            if (item != null)
            {
                Ctx.Remove(item);
                Ctx.SaveChanges();
            }

            if (Cfg.FeatureManagement.PublishEvents)
            {
                Console.WriteLine("Publishing event to Service Bus - mock");
            }

            return Ok();
        }

        [HttpPatch("{id}/update-instock")]
        public ActionResult<FoodItem> UpdateInStock(int id, [FromQuery] int amount)
        {
            var item = Ctx.Food.FirstOrDefault(f => f.ID == id);
            if (item == null)
                return NotFound();
            item.InStock += amount;
            Ctx.SaveChanges();
            return Ok(item);
        }
    }
}
