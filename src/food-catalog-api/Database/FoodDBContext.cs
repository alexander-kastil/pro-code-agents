using System;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;

namespace FoodApi
{
    //To manage Migrations & create the DB go to console:
    //Add EF Core Tools: dotnet tool install --global dotnet-ef
    //dotnet restore
    //dotnet-ef migrations add MIGRATION-NAME
    //dotnet-ef database update

    public class FoodDBContext : DbContext //Use DbContext if not using Identity
    {
        public FoodDBContext(DbContextOptions<FoodDBContext> options) : base(options)
        {
            Database.EnsureCreated();
        }

        public DbSet<FoodItem> Food { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            List<FoodItem> list = new List<FoodItem>();
            list.Add(new FoodItem
            {
                ID = 1,
                Name = "Butter Chicken",
                InStock = 12,
                MinStock = 3,
                Price = 12m,
                Code = "btc",
                Description = "Tender chicken simmered in a smoky tomato-butter sauce that’s bright with garam masala. Each bite balances gentle heat with velvety richness, making it a comfort dish you’ll keep dipping naan into.",
                PictureUrl = "https://m365copilotdev.blob.core.windows.net/food/butter-chicken.jpg"
            });
            list.Add(new FoodItem
            {
                ID = 2,
                Name = "Blini with Salmon",
                InStock = 16,
                MinStock = 4,
                Price = 9m,
                Code = "bls",
                Description = "Fluffy buckwheat blini crowned with cool crème fraîche and ribbons of smoked salmon. The briny pop of capers and dill keeps every forkful light, elegant, and perfect for lingering brunches.",
                PictureUrl = "https://m365copilotdev.blob.core.windows.net/food/blini-with-salmon.jpg"
            });
            list.Add(new FoodItem
            {
                ID = 3,
                Name = "Wiener Schnitzel",
                InStock = 30,
                MinStock = 6,
                Price = 18m,
                Code = "ws",
                Description = "A paper-thin veal cutlet fried until the golden crust crackles at the first bite. Finished with a squeeze of lemon, it’s a plate that brings alpine coziness and Oktoberfest swagger to the table.",
                PictureUrl = "https://m365copilotdev.blob.core.windows.net/food/wiener-schnitzel.jpg"
            });
            list.Add(new FoodItem
            {
                ID = 4,
                Name = "Cevapcici",
                InStock = 20,
                MinStock = 5,
                Price = 11m,
                Code = "cvp",
                Description = "Small, spiced grilled beef-and-pork sausages that char at the edges and stay juicy inside. Serve with warm flatbread, tangy ajvar, and a shower of fresh parsley — perfect for sharing.",
                PictureUrl = "https://m365copilotdev.blob.core.windows.net/food/cevapcici.jpg"
            });
            list.Add(new FoodItem
            {
                ID = 5,
                Name = "Germknödel",
                InStock = 26,
                MinStock = 6,
                Price = 7m,
                Code = "gkn",
                Description = "A pillowy yeast dumpling filled with sweet plum jam, steamed until cloud-soft and finished with melted butter and a dusting of poppy seeds — alpine comfort in every spoonful.",
                PictureUrl = "https://m365copilotdev.blob.core.windows.net/food/germknoedel.jpg"
            });
            list.Add(new FoodItem
            {
                ID = 6,
                Name = "Greek Salad",
                InStock = 23,
                MinStock = 5,
                Price = 8m,
                Code = "grs",
                Description = "Crisp cucumber, ripe tomatoes, Kalamata olives and creamy feta tossed with oregano and olive oil. Bright, briny, and refreshing — the sunlit flavors of the Aegean on a plate.",
                PictureUrl = "https://m365copilotdev.blob.core.windows.net/food/greek-saled.jpg"
            });
            list.Add(new FoodItem
            {
                ID = 7,
                Name = "Spare Ribs",
                InStock = 13,
                MinStock = 3,
                Price = 16m,
                Code = "spr",
                Description = "Slow-cooked until the meat slips from the bone, glazed in a sticky, smoky sauce with a hint of sweetness. Pair with crisp slaw and plenty of napkins for the full experience.",
                PictureUrl = "https://m365copilotdev.blob.core.windows.net/food/spare-ribs.jpg"
            });
            list.Add(new FoodItem
            {
                ID = 8,
                Name = "Pad Ka Prao",
                InStock = 18,
                MinStock = 4,
                Price = 10m,
                Code = "pkp",
                Description = "A classic Thai street-food stir-fry of minced meat or tofu with garlic, fiery chiles and holy basil — pungent, savory, and finished with a runny fried egg on top. Serve with jasmine rice for maximum comfort.",
                PictureUrl = "https://m365copilotdev.blob.core.windows.net/food/pad-ka-prao.jpg"
            });
            list.Add(new FoodItem
            {
                ID = 9,
                Name = "Falaffel with Humus",
                InStock = 26,
                MinStock = 6,
                Price = 9m,
                Code = "flh",
                Description = "Crispy, golden falafel served alongside silky hummus, bright pickles and warm pita — a satisfying vegetarian plate packed with herbaceous crunch and creamy comfort.",
                PictureUrl = "https://m365copilotdev.blob.core.windows.net/food/falaffel.jpg"
            });
            modelBuilder.Entity<FoodItem>()
                .Property(food => food.Price)
                .HasPrecision(18, 2);
            modelBuilder.Entity<FoodItem>().HasData(list.ToArray());
        }
    }
}