CXX       := g++
CXXFLAGS  := -pedantic-errors -Wall -std=c++14
BUILD     := ./build
OBJ_DIR   := $(BUILD)/objects
TARGET    := player_rulebased-B
INCLUDE   := -I../common
LIBRARIES :=
SRC       := player_rulebased-B.cpp ../common/participant.cpp
ifeq ($(OS),Windows_NT)
# on Windows, need to link with WinSock2
LIBRARIES += -lws2_32
endif

OBJECTS := $(SRC:%.cpp=$(OBJ_DIR)/%.o)

all: build $(TARGET)
	@echo "Done."

$(OBJ_DIR)/%.o: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(TARGET): $(OBJECTS)
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(INCLUDE) $(LDFLAGS) -o $(TARGET) $(OBJECTS) $(LIBRARIES)

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