using System;
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using FoodApi;
using FoodApp;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Mvc.Authorization;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Identity.Web;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
IConfiguration Configuration = builder.Configuration;
builder.Services.AddSingleton<IConfiguration>(Configuration);
var cfg = Configuration.Get<FoodConfig>();

// App insights using Feature Flag
if (cfg.FeatureManagement.UseApplicationInsights)
{
    builder.Services.AddApplicationInsightsTelemetry(options =>
    {
        if (!string.IsNullOrWhiteSpace(cfg.ApplicationInsights?.ConnectionString))
        {
            options.ConnectionString = cfg.ApplicationInsights.ConnectionString;
        }
    });
    builder.Services.AddSingleton<AILogger>();
}

//Database
var connectionString = cfg.ConnectionStrings?.DefaultDatabase;


if (string.IsNullOrWhiteSpace(connectionString))
{
    throw new InvalidOperationException("Connection string 'DefaultDatabase' is not configured.");
}

builder.Services.AddDbContext<FoodDBContext>(options => options.UseSqlServer(connectionString));

//Microsoft Identity auth
var az = Configuration.GetSection("Azure");

builder.Services.AddControllers();

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "Food-Catalog-Api", Version = "v1" });
});

// Cors
builder.Services.AddCors(o => o.AddPolicy("nocors", builder =>
{
    builder
        .SetIsOriginAllowed(host => true)
        .AllowAnyMethod()
        .AllowAnyHeader()
        .AllowCredentials();
}));

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

// Swagger
app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "Food-Api");
    c.RoutePrefix = string.Empty;
});

//Cors and Routing
app.UseCors("nocors");

app.MapControllers();
app.Run();