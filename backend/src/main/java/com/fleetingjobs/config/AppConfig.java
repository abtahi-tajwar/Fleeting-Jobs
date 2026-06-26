package com.fleetingjobs.config;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;
import org.springframework.web.client.RestClient;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class AppConfig {

    @Bean
    public RestClient workerRestClient(@Value("${worker.base-url}") String workerBaseUrl) {
        ObjectMapper snakeCaseMapper = new ObjectMapper();
        snakeCaseMapper.setPropertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE);

        MappingJackson2HttpMessageConverter converter = new MappingJackson2HttpMessageConverter(snakeCaseMapper);

        return RestClient.builder()
                .baseUrl(workerBaseUrl)
                .messageConverters(messageConverters -> {
                    messageConverters.removeIf(MappingJackson2HttpMessageConverter.class::isInstance);
                    messageConverters.add(converter);
                })
                .build();
    }

    @Bean
    public WebMvcConfigurer corsConfigurer(@Value("${app.cors-origins}") String corsOrigins) {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                        .allowedOrigins(corsOrigins.split(","))
                        .allowedMethods("*")
                        .allowedHeaders("*");
            }
        };
    }
}
