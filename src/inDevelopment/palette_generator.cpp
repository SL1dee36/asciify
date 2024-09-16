#include <string>
#include <vector>
#include <map>
#include <SDL2/SDL.h>
#include <SDL2/SDL_ttf.h>
#include <ffi.h>

struct palette_type {
    char character; 
    SDL_Color* colors;
};

extern "C" void create_palette(int color_lvl, const char* ascii_chars, void* output_palette) {
    if (TTF_Init() == -1) {
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "TTF_Init: %s", TTF_GetError());
        return;
    }

    TTF_Font* font = TTF_OpenFont("arial.ttf", 12); 
    if (font == NULL) {
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "TTF_OpenFont: %s", TTF_GetError());
        TTF_Quit();
        return;
    }

    std::map<char, std::map<SDL_Color, SDL_Surface*>> palette; 

    int color_step = 256 / color_lvl; 
    for (int r = 0; r < 256; r += color_step) {
        for (int g = 0; g < 256; g += color_step) {
            for (int b = 0; b < 256; b += color_step) {
                SDL_Color color = {r, g, b, 255};

                for (int i = 0; i < strlen(ascii_chars); i++) {
                    SDL_Surface* text_surface = TTF_RenderText_Solid(font, &ascii_chars[i], color);
                    palette[ascii_chars[i]][color] = text_surface;
                }
            }
        }
    }

    ffi_type* char_type = &ffi_type_char;
    ffi_type* sdl_color_type = ffi_type_struct(sizeof(SDL_Color), 
        "r", &ffi_type_sint32,
        "g", &ffi_type_sint32,
        "b", &ffi_type_sint32,
        "a", &ffi_type_sint32,
        NULL); 
    ffi_type* sdl_surface_type = &ffi_type_pointer;

    ffi_type* palette_type = ffi_type_struct(0, NULL);
    palette_type->elements = ffi_type_malloc(sizeof(ffi_type) * (1 + strlen(ascii_chars)));
    palette_type->elements[0] = char_type; 

    for (int i = 1; i <= strlen(ascii_chars); i++) {
        palette_type->elements[i] = ffi_type_pointer; 
    } 

    ffi_cif cif;
    ffi_cif_init(&cif, FFI_TYPE_VOID, NULL, palette_type, 1); 

    void* dst_palette = (void *)output_palette;

    palette_type* temp_palette = (palette_type*)malloc(sizeof(palette_type) * strlen(ascii_chars));
    for (int i = 0; i < strlen(ascii_chars); i++) {
        temp_palette[i].character = ascii_chars[i];
        temp_palette[i].colors = (SDL_Color*)malloc(sizeof(SDL_Color) * (color_lvl * color_lvl * color_lvl));
        int color_idx = 0;
        for (auto const& [key, value] : palette[ascii_chars[i]]) {
            temp_palette[i].colors[color_idx++] = key;
        }
    }

    ffi_call(&cif, FFI_FN(create_palette), dst_palette, color_lvl, ascii_chars, temp_palette); 

    for (int i = 0; i < strlen(ascii_chars); i++) {
        free(temp_palette[i].colors);
    }
    free(temp_palette);

    TTF_CloseFont(font);
    TTF_Quit();
}