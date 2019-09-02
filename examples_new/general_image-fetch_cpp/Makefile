CXX       := g++
CXXFLAGS  := -pedantic-errors -Wall -std=c++14
BUILD     := ./build
OBJ_DIR   := $(BUILD)/objects
TARGET    := general_image-fetch
INCLUDE   := -I../common -I../extlibs/cppcodec
LIBRARIES := -lopencv_core -lopencvhighgui
SRC       := general_image-fetch.cpp ../common/participant.cpp

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
