#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>

using namespace std;

template<typename T>
vector< vector<T> > read_csv(string path) {
  ifstream file;
  file.open("cell_pca_data.csv");
  string txt = "";
  string line;
  while ( getline (file,line) ) {
    txt += line + '\n';
  }
  int width(0);
  int height(0);
  vector<vector<T> > data;
  for ( int i = 0; i < 100; i ++) {
    cout << txt[i];
    if ( height == 0 and txt[i] == ',' ) {
      width ++;
    }
    if ( txt[i] == '\n' ) {
      height ++;
    }
  }
  cout << endl;
  cout << width << endl;
  cout << height << endl;
}

int main() {
  vector<vector<int> > v = read_csv<int>("cell_pca_data.csv");
}
