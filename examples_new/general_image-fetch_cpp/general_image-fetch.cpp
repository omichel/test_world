#include "participant.hpp"

#include <cppcodec/base64_rfc4648.hpp>
#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <iostream>

class ImageFetch : public aiwc::Participant {
  static constexpr std::size_t BYTES_PER_PIXEL = 4;

public:
  ImageFetch(char **argv) : aiwc::Participant(argv) {}
  virtual ~ImageFetch() {}

  void init() override {
    // initialize variables to store image
    // do not directly modify 'img_bgr' image updates are done in a way that
    // only the parts of the old frame that have been changed are overwritten by the new data
    img_bgr.clear();
    img_bgr.resize(info.resolution[X] * info.resolution[Y] * BYTES_PER_PIXEL);
    cv_img = cv::Mat(info.resolution[Y], info.resolution[X], CV_8UC3, &img_bgr[0]);

    cv::namedWindow("Frame", 1);
    cv::imshow("Frame", cv_img);
    cv::waitKey(1);
  }

  void update(aiwc::game_frame frame) override {
    auto pixel_ptr = [&](auto& img, std::size_t x, std::size_t y) {
      return &img[(info.resolution[X] * y + x) * BYTES_PER_PIXEL];
    };

    // fetch received subimages and construct a new frame
    // subimages are small regions on the new image
    // where some changes occurred since the last frame
    for(const auto& sub : frame.subimages) {
      // the subframe data are encoded with base64 scheme
      const auto decoded = cppcodec::base64_rfc4648::decode(sub.base64);
      assert(decoded.size() == (sub.w * sub.h * BYTES_PER_PIXEL));

      auto* decoded_ptr = &decoded[0];

      // paste the fetched subframe into the frame data you already have
      // to update the image frame
      for(std::size_t y = 0; y < sub.h; ++y) {
        std::memcpy(pixel_ptr(img_bgr, sub.x, sub.y + y),
                    decoded_ptr,
                    sub.w * BYTES_PER_PIXEL);
        decoded_ptr += sub.w * BYTES_PER_PIXEL;
      }
    }

    // now img_bgr contains the updated frame
    cv::imshow("Frame", cv_img);
    cv::waitKey(1);

    if(frame.reset_reason == aiwc::GAME_END) {
      // game is finished. finish() will be called after you return.
      // now you have about 30 seconds before this process is killed.
      std::cout << "Game ended : " << frame.time << std::endl;
      return;
    }
  }

  void finish(aiwc::game_frame frame) override {

  }

  private: // member variable
    std::vector<unsigned char> img_bgr;
    cv::Mat cv_img;
};

int main(int argc, char **argv) {
  ImageFetch *participant = new ImageFetch(argv);
  participant->run();
  delete participant;
  return 0;
}
