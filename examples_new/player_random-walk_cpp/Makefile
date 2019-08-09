CXX      := g++
CXXFLAGS := -pedantic-errors -Wall -std=c++11
BUILD    := ./build
OBJ_DIR  := $(BUILD)/objects
TARGET   := player_random-walk
INCLUDE  := -I../common
SRC      := player_random-walk.cpp ../common/player.cpp

OBJECTS := $(SRC:%.cpp=$(OBJ_DIR)/%.o)

all: build $(TARGET)
	@echo "Done."

$(OBJ_DIR)/%.o: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(TARGET): $(OBJECTS)
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(INCLUDE) $(LDFLAGS) -o $(TARGET) $(OBJECTS)

.PHONY: all build clean debug release

build:
	@mkdir -p $(OBJ_DIR)

debug: CXXFLAGS += -DDEBUG -g
debug: all

release: CXXFLAGS += -O2
release: all

clean:
	-@rm -rvf $(BUILD)
	-@rm -rvf $(TARGET)
